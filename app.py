import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="LLM Chatbot", layout="centered")
st.title("🤖 LLM Chatbot")

# -----------------------------
# Session state initialization
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

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
            data = {"query": user_input}

            if uploaded_file:
                files["file"] = (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )

            response = requests.post(
                BACKEND_URL,
                data=data,
                files=files if files else None,
            )

            if response.status_code == 200:
                result = response.json()

                assistant_reply = (
                    f"Intent: {result['intent']}\n\n"
                    f"Response: {result['response']}"
                )
            else:
                assistant_reply = "❌ Backend error."

        st.markdown(assistant_reply)

    # ---- Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )
