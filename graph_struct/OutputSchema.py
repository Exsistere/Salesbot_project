from pydantic import BaseModel
from typing import Literal


class GuardrailIntent(BaseModel):
    intent_type: Literal["META", "ATTACK"]