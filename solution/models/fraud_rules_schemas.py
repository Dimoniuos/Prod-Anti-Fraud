from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class FraudRule(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    dslExpression: str = Field(min_length=3, max_length=2000)
    enabled: bool = True
    priority: int = Field(default=100, ge=1)


class FraudRuleUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    dslExpression: str = Field(min_length=3, max_length=2000)
    enabled: bool
    priority: int = Field(ge=1)

class Rule(BaseModel):
    dslExpression: str = Field(min_length=3, max_length=2000)

class DSLError(BaseModel):
    code: str
    message: str
    position: Optional[int] = None
    near: Optional[str] = None

class DSLValidateResponse(BaseModel):
    isValid: bool
    normalizedExpression: Optional[str]
    errors: List[DSLError]