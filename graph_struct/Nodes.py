from graph_struct import llm
from graph_struct import state
from graph_struct import OutputSchema
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from RAG import rag
import json
import os
                   
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "prompt.json")
def load_prompts():
    with open(file_path,"r",encoding="utf-8") as f:
        return json.load(f)

prompts = load_prompts()

async def GuardRail(state: state.State):
    print("at guard rail node")
    GUARDRAIL_PROMPT = prompts["guardrail"]["prompt"].format(query=state["query"])
    # guardrail_llm = llm.gemini_llm_model.with_structured_output(OutputSchema.GuardrailIntent)
    # result: OutputSchema.GuardrailIntent = guardrail_llm.invoke(
    #     GUARDRAIL_PROMPT.format(query=state["query"])
    #)
    result= await llm.gemini_llm_model.create(messages=[UserMessage(content=GUARDRAIL_PROMPT, source="system")],
                                              json_output=OutputSchema.GuardrailIntent)
    
    # Convert to object first, then get attribute
    intent = OutputSchema.GuardrailIntent.model_validate_json(result.content).intent_type

 
    print(intent)
    return{
        "intent_type": intent
        #"intent_type": result.content.intent_type
    }

def guardrail_router(state: state.State) -> str:
    print("at guardrail router")
    return state["intent_type"]

async def attack_query(state: state.State):
    print("attack path")
    if state["intent_type"] == "ATTACK":
        #generate normal response
        ATTACKQUERY_PROMPT = prompts["attackquery"]["prompt"].format(query=state["query"])
        # attack_query_llm = llm.gemini_llm_model
        # result = attack_query_llm.invoke(
        #     ATTACKQUERY_PROMPT.format(query=state["query"])
        #)
        result= await llm.gemini_llm_model.create(messages=[UserMessage(content=ATTACKQUERY_PROMPT, source="system")]) 
        return{
            "response": result
        }
async def Classifier(state: state.State):
    if state["intent_type"] == "META":
        CLASSIFIER_PROMPT= prompts["classifier"]["prompt"].format(query=state["query"])
        result = await llm.gemini_llm_model.create(messages=[UserMessage(content=CLASSIFIER_PROMPT, source="system")], json_output=OutputSchema.MetaClassifier)
        meta_type = OutputSchema.MetaClassifier.model_validate_json(result.content).meta_query_type
        print("meta type:", meta_type)
        return{
            "meta_type" : meta_type
        } 
def classifier_router(state: state.State):
    print("at classifier router")
    return(state["meta_type"])
async def SalesNode(state: state.State):
    print("Sales Node")
    SALES_PROMPT=prompts["salesprompt"]["prompt"].format(query=state["query"],context=rag.query_retrival(state["query"]))
    result = await llm.gemini_llm_model.create(messages=[UserMessage(content=SALES_PROMPT, source="system")])
    return {
        "response": result
    }
     

async def LeadDetails(state: state.State):
    BOOKING_EXTRACT_PROMPT=prompts["booking_extraction"]["prompt"].replace("{query}", state["query"])
    result = await llm.gemini_llm_model.create(messages=[UserMessage(content=BOOKING_EXTRACT_PROMPT, source="system")], json_output=OutputSchema.BookingInfo)
    booking_details = OutputSchema.BookingInfo.model_validate_json(result.content)
    return booking_details

async def BookingNode(state: state.State):
    print("booking extraction node")
    BOOKING_EXTRACT_PROMPT=prompts["booking_extraction"]["prompt"].replace("{query}", state["query"])
    result = await llm.gemini_llm_model.create(messages=[UserMessage(content=BOOKING_EXTRACT_PROMPT, source="system")], json_output=OutputSchema.LeadDetails)
    booking_details = OutputSchema.LeadDetails.model_validate_json(result.content)
    return{
        "response" : result,
        "extracted_details": booking_details,
        "active_flow": "booking"
    }
def route_from_start(state: state.State):
    if state.get("active_flow") == "booking":
        return "booking"
    return "start"

async def Booking_follow_up(state: state.State):
    extracted = dict(state["extracted_details"])
    print(extracted)
    missing_fields = [
        field for field,value in extracted.items()
        if value is None
    ]
    BOOKING_FOLLOWUP_PROMPT = prompts["booking_followup"]["prompt"].replace("{missing_fields}", ' '.join(missing_fields))
    result = await llm.gemini_llm_model.create(messages=[UserMessage(content=BOOKING_FOLLOWUP_PROMPT, source="system")])
    return{
        "response": result
    }
    
async def Booking_query_classifier(state: state.State):
    BOOKING_CLASSIFIER_PROMPT = prompts["booking_classifier"]["prompt"].replace("{query}",state["query"])
    result = await llm.gemini_llm_model.create(messages=[UserMessage(content=BOOKING_CLASSIFIER_PROMPT, source="system")], json_output=OutputSchema.BookingQueryClassifier)
    type = OutputSchema.BookingQueryClassifier.model_validate_json(result.content).intent_type
    return{
        "booking_query_type": type
    }

def Booking_query_router(state: state.State):
    return state["booking_query_type"]

async def Booking_exit_response(state: state.State):   
    booking_details = dict(state["extracted_details"])
    BOOKING_RESPONSE_PROMPT = prompts["booking_response"]["prompt"].format(name=booking_details["name"],email=booking_details["email"],phone_number=booking_details["phone_number"])
    result = await llm.gemini_llm_model.create(messages=[UserMessage(content=BOOKING_RESPONSE_PROMPT, source="system")])
    print("active flow changed to start")
    return{
        "response": result.content,
        "active_flow": "start"
    }