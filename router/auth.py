from fastapi import FastAPI,APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import JWTError,jwt
from sqlalchemy.orm import Session
from fastapi.responses import Response
from passlib.context import CryptContext
from typing import Annotated
from fastapi.responses import JSONResponse
from datetime import timedelta,timezone,datetime
from database import SessionLocal
from models import Users
from schemas import CreateUser,UpdateUser
router = APIRouter(prefix="/auth")

bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/login')

SECRET_KEY = '751e63b2d653ae6e369c968122841f0349866a997d56ac45f51cf331ebdb014f'
ALGORITHM = "HS256"
def authenticate_user(username,password,db):
    user=db.query(Users).filter(Users.username == username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password,user.hash_password):
        return user
    return False


def create_access_token(username:str,user_id:int,expire_delta:timedelta):
    encodes={'sub':username,'id':user_id}
    expires=datetime.now(timezone.utc)+expire_delta
    encodes.update({'exp':expires})
    return jwt.encode(encodes,SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(token:Annotated[str,Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get('sub')
        user_id:int=payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=404,detail='user not found')
        return{'username': username,'id':user_id}
    except:
        raise HTTPException(status_code=404,detail='user not found')
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]

@router.post('/register')
def register_user(db:db_dependency,new_user:CreateUser):
    existing_user = db.query(Users).filter(Users.username==new_user.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=400,detail="User already Exists")
    
    existing_user_email = db.query(Users).filter(Users.email==new_user.email).first()
    if existing_user_email is not None:
        raise HTTPException(status_code=400,detail="Email already Exists")
    
    user_model = Users(**new_user.model_dump(exclude={"password"}),
                       hash_password=bcrypt_context.hash(new_user.password))
    db.add(user_model)
    db.commit()
    return JSONResponse(status_code=201,content={'message': 'User created successfully'})
# @router.post("/register")
# def register_user(
#     db: db_dependency,
#     new_user: CreateUser
# ):

#     # 1. Check username
#     existing_user = db.query(Users).filter(
#         Users.username == new_user.username
#     ).first()

#     if existing_user is not None:
#         raise HTTPException(
#             status_code=400,
#             detail="User already exists"
#         )

#     # 2. Check email
#     existing_email = db.query(Users).filter(
#         Users.email == new_user.email
#     ).first()

#     if existing_email is not None:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already exists"
#         )

#     # 3. Hash password
#     hashed_password = bcrypt_context.hash(
#         new_user.password
#     )

#     # 4. Create user
#     user_model = Users(
#         username=new_user.username,
#         email=new_user.email,
#         hash_password=hashed_password
#     )

#     # 5. Add to database
#     db.add(user_model)

#     # 6. Save database
#     db.commit()

#     # 7. Refresh object
#     db.refresh(user_model)

#     return {
#         "message": "User created successfully"
#     }

@router.post('/login')
def login_user(db:db_dependency,form_user:Annotated[OAuth2PasswordRequestForm,Depends()]):
    user=authenticate_user(form_user.username,form_user.password,db)
    if not user:
        raise HTTPException(status_code=401,detail="Incorrect username or password")
    token = create_access_token(user.username,user.id,timedelta(minutes=30))
    return {'access_token':token,'token_type':'bearer'}