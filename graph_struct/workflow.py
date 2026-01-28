from langgraph.graph import StateGraph
from langgraph.graph import START, END
from graph_struct import Nodes
from graph_struct import state
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

builder = StateGraph(state.State)
builder.add_node("GuardRail", Nodes.GuardRail)
builder.add_node("attackquery", Nodes.attack_query)
builder.add_node("classifier", Nodes.Classifier)
builder.add_node("sales", Nodes.SalesNode)
builder.add_node("booking", Nodes.BookingNode)
builder.add_node("Booking_followup", Nodes.Booking_follow_up)
builder.add_node("Booking_query_classifier",Nodes.Booking_query_classifier)
builder.add_node("Booking_exit_response", Nodes.Booking_exit_response)

builder.add_conditional_edges(
    START,
    Nodes.route_from_start,
    {
        "booking":"booking",
        "start":"GuardRail"
    }
)
builder.add_conditional_edges(
    "GuardRail",
    Nodes.guardrail_router,
    {
        "ATTACK":"attackquery",
        "META":"classifier"
    }
)
builder.add_conditional_edges(
    "classifier",
    Nodes.classifier_router,
    {
        "SALES": "sales",
        "BOOKING": "booking"
    }
)
builder.add_edge("booking", "Booking_followup")

builder.add_edge("Booking_followup","Booking_query_classifier")
builder.add_conditional_edges(
    "Booking_query_classifier",
    Nodes.Booking_query_router,
    {
        "FOLLOWUP": END,
        "END": "Booking_exit_response"
    }
)
builder.add_edge("sales",END)
builder.add_edge("Booking_exit_response",END)
builder.add_edge("attackquery",END) 

grap = builder.compile(checkpointer=checkpointer)

async def Workflow(user_input:str, session_id:str):
    return await grap.ainvoke(
        {"query": user_input},
        config={
            "configurable":{
                "thread_id": session_id
            }
        }     
    )



# async def Workflow(user_input, state: state.State | None = None
#                    ):
#     if state is None:
#         state = {
#             "query": user_input
#             }
#     else:
#         state["query"] = user_input

#     return await grap.ainvoke(state)
    





    # if state is None: 
    #     return await grap.ainvoke({"query":user_input, "active_flow":"start"})
    # else:
    #     return await grap.ainvoke({"query":user_input})

# # User input
# query: str

# # Guardrail classification
# intent_type: Optional[Literal["META", "ATTACK"]]

# # Meta query classification
# meta_type: Optional[Literal["SALES", "BOOKING"]]

# # Final model response
# response: Optional[str]
