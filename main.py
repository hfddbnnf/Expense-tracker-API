from fastapi import FastAPI,Depends,HTTPException
from typing import Annotated,Optional
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from database import Base,engine
from router import auth,transactions
app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(transactions.router)
@app.get('/')
def root():
    return{"message": "Expense Tracker is running"}