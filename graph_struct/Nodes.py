from graph_struct import llm
from graph_struct import state
from graph_struct import OutputSchema
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "prompt.json")
def load_prompts():
    with open(file_path,"r",encoding="utf-8") as f:
        return json.load(f)

prompts = load_prompts()

def GuardRail(state: state.State):
    GUARDRAIL_PROMPT = prompts["guardrail"]["prompt"]
    guardrail_llm = llm.gemini_llm_model.with_structured_output(OutputSchema.GuardrailIntent)
    result: OutputSchema.GuardrailIntent = guardrail_llm.invoke(
        GUARDRAIL_PROMPT.format(query=state["query"])
    )
    return{
        "intent_type": result.intent_type
    }

def Classifier(state: state.State):
    pass

def SalesNode(state: state.State):
    pass

def BookingNode(state: state.State):
    pass