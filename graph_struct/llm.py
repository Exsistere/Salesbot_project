from langchain_google_genai import ChatGoogleGenerativeAI
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
import os

gemini_llm_model = OpenAIChatCompletionClient(
    model="openai/gpt-oss-120b",
    api_key="REMOVED",
    base_url="https://api.groq.com/openai/v1",
    model_info=ModelInfo(
        model_name="llama-3.1-8b-instant",
        provider="groq",
        family="llama",
        max_context_length=8192,
        function_calling=True,
        json_output=True,
        vision=False,
        structured_output=True
    ),
)
# gemini_llm_model = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )


#REMOVED