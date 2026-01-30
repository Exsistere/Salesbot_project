import streamlit as st
import requests
import uuid
import json
BACKEND_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="LLM Chatbot", layout="centered")
st.title("🤖 LLM Chatbot")

# -----------------------------
# Session state initialization
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "lead_details" not in st.session_state:
    st.session_state.lead_details = {
        "name": None,
        "email": None,
        "date": None,
        "time": None,
        "product": None,
    }
if "lead_history" not in st.session_state:
    st.session_state.lead_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id=str(uuid.uuid4())

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "audio_consumed" not in st.session_state:
    st.session_state.audio_consumed = False

if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

if "tts_cache" not in st.session_state:
    st.session_state.tts_cache = {}  # msg_index -> audio_bytes

# # Graph state to persist LangGraph / booking flow
# if "graph_state" not in st.session_state:
#     st.session_state.graph_state = None  # Will store full state returned from backend

# ------------------------------
# sidebard 
# ------------------------------
with st.sidebar:
    st.header("Playground")
    st.subheader("Lead details")

    st.markdown(f"**Name:** {st.session_state.lead_details['name'] or '-'}")
    st.markdown(f"**Email:** {st.session_state.lead_details['email'] or '-'}")
    st.markdown(f"**Date:** {st.session_state.lead_details['date'] or '-'}")
    st.markdown(f"**Time:** {st.session_state.lead_details['time'] or '-'}")
    st.markdown(f"**Product:** {st.session_state.lead_details['product'] or '-'}")

    st.divider()

    st.subheader("🕘 Lead History")
    if st.session_state.lead_history:
        for idx, lead in enumerate(st.session_state.lead_history[::-1], 1):
            with st.expander(f"Lead #{len(st.session_state.lead_history) - idx + 1}"):
                st.write(lead)
    elif len(st.session_state.lead_history) == 0:
        st.caption("No leads captured yet.")







# -----------------------------
# Display chat history
# -----------------------------
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Only show TTS for assistant messages
        if msg["role"] == "assistant":
            col1, col2 = st.columns([1, 6])
            with col1:
                if msg["content"].strip():
                    if st.button("🔊 Read aloud", key=f"tts_{idx}"):
                        if "tts_cache" not in st.session_state:
                            st.session_state.tts_cache = {}

                        if idx not in st.session_state.tts_cache:
                            payload = {"text": msg["content"]}
                            tts_resp = requests.post(
                                "http://localhost:8000/tts",
                                json=payload,
                                headers={"Content-Type": "application/json"},
                            )

                            if tts_resp.status_code == 200:
                                st.session_state.tts_cache[idx] = tts_resp.content
                            else:
                                st.error(f"TTS failed: {tts_resp.status_code}")

            # Play cached audio if available
            if "tts_cache" in st.session_state and idx in st.session_state.tts_cache:
                st.audio(
                    st.session_state.tts_cache[idx],
                    format="audio/wav"
                )

# -----------------------------
# File uploader (per turn)
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload a PDF (optional)",
    type=["pdf"],
    key="pdf_uploader"
)


audio_file = st.audio_input(
    "Dictate",
    key=f"audio_{st.session_state.audio_key}"
    )
if audio_file and st.session_state.audio_bytes is None:
    st.session_state.audio_bytes = audio_file.read()  
    st.session_state.audio_consumed = False
# -----------------------------
# Chat input
# -----------------------------
user_input = st.chat_input("Ask something about sales or booking...")


if user_input or (st.session_state.audio_bytes and not st.session_state.audio_consumed):
    # ---- Show user message
    print(bool(audio_file))
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # ---- Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            files = {}
            # data = {
            #     "query": user_input,
            #     "state": st.session_state.graph_state
            # }

            # graph_state_serializable = None
            # if st.session_state.graph_state:
            #     try:
            #         graph_state_serializable = st.session_state.graph_state.model_dump()
            #     except AttributeError:
            #         graph_state_serializable = st.session_state.graph_state

            # # --- ALWAYS send form data ---
            # data_to_send = {
            #     "query": user_input,
            #     "state": json.dumps(graph_state_serializable) if graph_state_serializable else None
            # }

            data_to_send = {
                "query": user_input,
                "session_id": st.session_state.session_id
            }

            files = {}
            if uploaded_file:
                files["file"] = (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                )
            if st.session_state.audio_bytes and not st.session_state.audio_consumed:
                files["audio"] = (
                    "voice.wav",
                    st.session_state.audio_bytes,
                    audio_file.type
                )
                st.session_state.audio_consumed = True

            if not files: files = None
            response = requests.post(
                BACKEND_URL,
                data=data_to_send,
                files=files
            )

            if response.status_code == 200:
                print("response recieved from backend",response.status_code)
                st.session_state.audio_consumed = True
                st.session_state.audio_bytes = None
                st.session_state.audio_key += 1
                result = response.json()
                # st.session_state.graph_state = result.get("state", st.session_state.graph_state)
                assistant_reply = (
                    f"Intent: {result['intent']}\n\n"
                    f"Response: {result['response']}"
                )

                extracted = result.get("extracted_details",{})
                if extracted:
                    for key in st.session_state.lead_details:
                        if extracted.get(key):
                            st.session_state.lead_details[key] = extracted[key]
                
                    if extracted:
                        st.session_state.lead_history.append(extracted)

            else:
                assistant_reply = "❌ Backend error."

        st.markdown(assistant_reply)

    # ---- Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )
    # print("rerun hit")
    st.rerun()
