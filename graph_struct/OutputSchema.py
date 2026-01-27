from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional


class GuardrailIntent(BaseModel):
    intent_type: Literal["META", "ATTACK"]

class MetaClassifier(BaseModel):
    meta_query_type: Literal["SALES", "BOOKING"]

class BookingInfo(BaseModel):
    name: Optional[str] = Field(
        description= "Name of the customer"
    )
    email: Optional[EmailStr] = Field(
        description="Email address of the customer"
    )
    phone_number: Optional[str] = Field(
        description="Phone number of the customer"
    )

class LeadDetails(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    product: Optional[str] = None

class BookingQueryClassifier(BaseModel):
    intent_type: Literal["FOLLOWUP","END"]

