from pydantic import BaseModel
from typing import Literal


class GuardrailIntent(BaseModel):
    intent_type: Literal["META", "ATTACK"]

class MetaClassifier(BaseModel):
    meta_query_type: Literal["SALES", "BOOKING"]