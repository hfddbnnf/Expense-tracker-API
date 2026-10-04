from database import Base
from sqlalchemy import Date,Float,Integer,Column,String,ForeignKey
from sqlalchemy.orm import relationship
class Users(Base):
    __tablename__="users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,nullable=False)
    email = Column(String,unique=True,nullable=False)
    hash_password = Column(String,nullable=False)
    
class Transactions(Base):
    __tablename__="transactions"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    amount = Column(Float,nullable=False)
    type = Column(String,nullable=False)
    category = Column(String,nullable=False)
    date = Column(Date,nullable=False)
    owner_id = Column(Integer,ForeignKey("users.id"),nullable=False)
