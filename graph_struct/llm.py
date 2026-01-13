from langchain_google_genai import ChatGoogleGenerativeAI
import os
gemini_llm_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
