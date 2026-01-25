from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=72)
    fullName: str = Field(..., min_length=2, max_length=200)
    age: Optional[int] = Field(None, ge=18, le=120)
    region: Optional[str] = Field(None, max_length=32)
    gender: Optional[Literal["MALE", "FEMALE"]] = None
    maritalStatus: Optional[Literal["SINGLE", "MARRIED", "DIVORCED", "WIDOWED"]] = None

    @field_validator("password")
    def vaildate_password(cls, password: str):
        for x in password.lower():
            if ord(x) >= ord('a') or ord(x) <= ord('z'):
                break
        else:
            raise ValueError("Password must contain at least one letter.")
        for x in password:
            if x.isdigit():
                break
        else:
            raise ValueError("Password must contain at least one digit.")
        return password

class LoginRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    def vaildate_password(cls, password: str):
        for x in password.lower():
            if ord(x) >= ord('a') or ord(x) <= ord('z'):
                break
        else:
            raise ValueError("Password must contain at least one letter.")
        for x in password:
            if x.isdigit():
                break
        else:
            raise ValueError("Password must contain at least one digit.")
        return password

class RegisterRequestByAdmin(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=72)
    fullName: str = Field(..., min_length=2, max_length=200)
    age: Optional[int] = Field(None, ge=18, le=120)
    region: Optional[str] = Field(None, max_length=32)
    gender: Optional[Literal["MALE", "FEMALE"]] = None
    maritalStatus: Optional[Literal["SINGLE", "MARRIED", "DIVORCED", "WIDOWED"]] = None
    role: Optional[Literal["ADMIN", "USER"]]

    @field_validator("password")
    def vaildate_password(cls, password: str):
        for x in password.lower():
            if ord(x) >= ord('a') or ord(x) <= ord('z'):
                break
        else:
            raise ValueError("Password must contain at least one letter.")
        for x in password:
            if x.isdigit():
                break
        else:
            raise ValueError("Password must contain at least one digit.")
        return password


class UserUpdateBase(BaseModel):
    fullName: str = Field(..., min_length=2, max_length=200)
    age: Optional[int] = Field(..., ge=18, le=120)
    region: Optional[str] = Field(..., max_length=32)
    gender: Optional[Literal["MALE", "FEMALE"]] = ...
    maritalStatus: Optional[Literal["SINGLE", "MARRIED", "DIVORCED", "WIDOWED"]] = ...

class UserUpdateAdmin(UserUpdateBase):
    role: Optional[Literal["USER", "ADMIN"]] = None
    isActive: Optional[bool] = None