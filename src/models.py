from pydantic import BaseModel
from enum import Enum


class TypeCommission(str, Enum):
    continuous_commission = "continuous_commission"
    sporadic_commission = "sporadic_commission"
    high_cost_commission = "high_cost_commission"


class TypeRole(str, Enum):
    RM = "RM"
    RD = "RD"
    RP1 = "RP1"
    RP2 = "RP2"
    RP3 = "RP3"
    RG = "RG"
    RC = "RC"
    RV = "RV"


class Commission(BaseModel):
    type_commission: TypeCommission
    value: float


class User(BaseModel):
    role: TypeRole
    name: str


class Role(BaseModel):
    role: TypeRole
