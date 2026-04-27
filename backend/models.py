from pydantic import BaseModel
from typing import List

class UserSignup(BaseModel):
    fullname: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Alternative(BaseModel):
    name: str
    price: float
    pharmacy: str
    dist: float

class Medicine(BaseModel):
    name: str
    formula: str
    price: float
    company: str
    alternatives: List[Alternative]

class ContactRequest(BaseModel):
    name: str
    email: str
    description: str
