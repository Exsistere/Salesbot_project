from typing import TypedDict, Optional, Literal
from graph_struct.OutputSchema import LeadDetails
class State(TypedDict):

    # User input
    query: str

    # Guardrail classification
    intent_type: Optional[Literal["META", "ATTACK"]]

    # Meta query classification
    meta_type: Optional[Literal["SALES", "BOOKING"]]

    #user details
    extracted_details: Optional[LeadDetails]

    booking_query_type: Optional[Literal["FOLLOWUP", "END"]]

    active_flow: Literal["start", "booking"]
    # Final model response
    response: Optional[str]
