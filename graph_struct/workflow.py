from langgraph.graph import StateGraph
from langgraph.graph import START, END
from graph_struct import Nodes
from graph_struct import state

builder = StateGraph(state.State)
builder.add_node("GuardRail", Nodes.GuardRail)
builder.add_node("attackquery", Nodes.attack_query)
builder.add_node("classifier", Nodes.Classifier)
builder.add_node("sales", Nodes.SalesNode)
builder.add_node("booking", Nodes.BookingNode)

builder.add_edge(START, "GuardRail")
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
builder.add_edge("sales",END)
builder.add_edge("booking",END)
builder.add_edge("attackquery",END)

grap = builder.compile()

# def Workflow(user_input):
#     return grap.invoke({"query":user_input})
async def Workflow(user_input):
    return await grap.ainvoke({"query":user_input})

# # User input
# query: str

# # Guardrail classification
# intent_type: Optional[Literal["META", "ATTACK"]]

# # Meta query classification
# meta_type: Optional[Literal["SALES", "BOOKING"]]

# # Final model response
# response: Optional[str]
