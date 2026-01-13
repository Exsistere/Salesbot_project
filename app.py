import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="LLM Chatbot", layout="centered")

st.title("🤖 LLM Chatbot")

# --- User input ---
query = st.text_area(
    "Enter your query",
    placeholder="Ask something about sales or booking...",
)

uploaded_file = st.file_uploader(
    "Upload a PDF (optional)",
    type=["pdf"]
)

# --- Submit ---
if st.button("Send"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Thinking..."):
            files = {}
            data = {"query": query}

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
            st.success("Response received")
            st.markdown("### 💬 LLM Response")
            st.write(result["response"])
        else:
            st.error("Backend error")
