from typing import TypedDict, Optional, Literal

class State(TypedDict):

    # User input
    query: str

    # Guardrail classification
    intent_type: Optional[Literal["META", "ATTACK"]]

    # Meta query classification
    meta_type: Optional[Literal["SALES", "BOOKING"]]

    # Final model response
    response: Optional[str]
