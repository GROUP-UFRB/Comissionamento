from pydantic import BaseModel

from typing import Literal

TypeRole = Literal["RM", "RD", "RP1", "RP2", "RP3", "RG", "RC", "RV"]


class User(BaseModel):
    role: TypeRole
    name: str


class Role(BaseModel):
    role: TypeRole


class Commission(BaseModel):
    type_commission: Literal["continuous", "sporadic", "high_cost"]
    value: float
    user: User
