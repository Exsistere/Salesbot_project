from langgraph.graph import StateGraph
from langgraph.graph import START, END
from graph_struct import Nodes
from graph_struct import state

builder = StateGraph(state.State)
builder.add_node("Guard Rail", Nodes.GuardRail)
builder.add_edge(START, "Guard Rail")
builder.add_edge("Guard Rail",END)

grap = builder.compile()

def Workflow(user_input):
    return grap.invoke({"query":user_input, "intent_type":None, "meta_type":None, "response": None})


# # User input
# query: str

# # Guardrail classification
# intent_type: Optional[Literal["META", "ATTACK"]]

# # Meta query classification
# meta_type: Optional[Literal["SALES", "BOOKING"]]

# # Final model response
# response: Optional[str]
