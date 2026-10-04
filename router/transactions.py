from typing import Annotated,Optional
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Transactions
from fastapi.responses import JSONResponse
from router.auth import get_current_user
from schemas import TransactionCreate,TransactionResponse,TransactionUpdate
router = APIRouter(prefix="/transactions")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency  = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.post("/create")
def create_transaction(user:user_dependency,db:db_dependency,new_transaction:TransactionCreate):
    transaction_model = Transactions(**new_transaction.model_dump(),owner_id=user.get("id"))
    db.add(transaction_model)
    db.commit()
    return JSONResponse(status_code=201,content={'message':'Transactions create successfully'})
@router.get("")
def get_transactin(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')
    return db.query(Transactions).filter(Transactions.owner_id == user.get('id')).all()

@router.get("/{transaction_id}")
def get_specific_transaction(user:user_dependency,db:db_dependency,transaction_id:int):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')
    specific_transaction=db.query(Transactions).filter(Transactions.id==transaction_id,Transactions.owner_id == user.get('id')).first()
    if specific_transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')
    return specific_transaction

@router.put("/edit/{transaction_id}")
def update_transactions(user:user_dependency,db:db_dependency,transaction_id:int,update_transaction:TransactionUpdate):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')
    transactions=db.query(Transactions).filter(Transactions.id==transaction_id,Transactions.owner_id == user.get('id')).first()
    if transactions is None:
        raise HTTPException(status_code=404, detail='Transaction not found')
    update_data = update_transaction.model_dump(exclude_unset=True)
    for key,value in update_data.items():
        setattr(transactions,key,value)
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'To do updated successfully'})

@router.delete("/delete/{transaction_id}")
def delete_transaction(user:user_dependency,db:db_dependency,transaction_id:int):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')
    transaction = db.query(Transactions).filter(Transactions.id==transaction_id,Transactions.owner_id==user.get('id')).first()
    if transaction is None:
        raise HTTPException(status_code=404,detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Transactions deleted successfully'})

@router.get("/filter")
def filter_transaction(user:user_dependency,db:db_dependency,type:Optional[str]=None,category:Optional[str]=None,minimum_amount:Optional[float]=None,maximum_amount:Optional[float]=None):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')
    query =db.query(Transactions).filter(Transactions.owner_id==user.get('id'))
    
    if type is not None:
        if type not in ["income", "expense"]:
            raise HTTPException( status_code=400, detail="Type must be income or expense")
        

        query = query .filter(
            Transactions.type == type
        )
    if category is not None:
        query = query .filter(Transactions.category==category)

    if minimum_amount is not None:

        if minimum_amount < 0:

            raise HTTPException(
                status_code=400,
                detail="minimum_amount cannot be negative"
            )

        query = query.filter(
            Transactions.amount >= minimum_amount
        )


    if maximum_amount is not None:

        if maximum_amount < 0:

            raise HTTPException(
                status_code=400,
                detail="maximum_amount cannot be negative"
            )

        query = query.filter(
            Transactions.amount <= maximum_amount
        )


    if (
        minimum_amount is not None
        and maximum_amount is not None
        and minimum_amount > maximum_amount
    ):

        raise HTTPException(
            status_code=400,
            detail="minimum_amount cannot be greater than maximum_amount"
        )


    return query.all()