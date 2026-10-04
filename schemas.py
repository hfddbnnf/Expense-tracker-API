from datetime import date as Date
from pydantic import BaseModel,Field,EmailStr
from typing import Optional,Literal

class CreateUser(BaseModel):
    username : str = Field(min_length=3,max_length=50)
    email : EmailStr
    password : str = Field(min_length=5)

class UpdateUser(BaseModel):
    username: str
    email: EmailStr

class TransactionCreate(BaseModel):
    title:str=Field(min_length=1,max_length=100)
    amount:float=Field(gt=0)
    type:Literal['income','expense']
    category:str=Field(min_length=1,max_length=50)
    date:Date=Field(default_factory=Date.today)

class TransactionUpdate(BaseModel):
    title:Optional[str]=Field(default=None,min_length=1,max_length=100)
    amount:Optional[float]=Field(default=None,gt=0)
    type:Optional[Literal['income','expense']] = None
    category:Optional[str]=Field(default=None,min_length=1,max_length=50)
    date:Optional[Date]=None

class TransactionResponse(BaseModel):
    id: int
    title: str
    amount: float
    type: Literal["income", "expense"]
    category: str
    date: Date
    owner_id: int
