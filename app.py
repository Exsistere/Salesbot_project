import streamlit as st
import requests
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

# Graph state to persist LangGraph / booking flow
if "graph_state" not in st.session_state:
    st.session_state.graph_state = None  # Will store full state returned from backend

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
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# File uploader (per turn)
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload a PDF (optional)",
    type=["pdf"],
    key="pdf_uploader"
)

# -----------------------------
# Chat input
# -----------------------------
user_input = st.chat_input("Ask something about sales or booking...")


if user_input:
    # ---- Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # ---- Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            files = {}
            data = {
                "query": user_input,
                "state": st.session_state.graph_state
            }

            graph_state_serializable = None
            if st.session_state.graph_state:
                try:
                    graph_state_serializable = st.session_state.graph_state.model_dump()
                except AttributeError:
                    graph_state_serializable = st.session_state.graph_state

            # --- ALWAYS send form data ---
            data_to_send = {
                "query": user_input,
                "state": json.dumps(graph_state_serializable) if graph_state_serializable else None
            }

            files = None
            if uploaded_file:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }
            
            response = requests.post(
                BACKEND_URL,
                data=data_to_send,
                files=files
            )

            if response.status_code == 200:
                result = response.json()
                st.session_state.graph_state = result.get("state", st.session_state.graph_state)
                assistant_reply = (
                    f"Intent: {result['intent']}\n\n"
                    f"Response: {result['response']}"
                )

                extracted = result.get("extracted_details",{})
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
    
    st.rerun()
