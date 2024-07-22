import requests as req
from utils.environment import BACKEND_URL
from utils import models
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from . import schema
import uuid
from utils.utils import hash_password, check_password

def get_user_by_id(db:Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db:Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_users(db:Session, skip:int = 0, limit:int = 0):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db:Session, user: schema.UserCreate):
    password = hash_password(user.password)
    db_user = models.User(
        id=uuid.uuid4(),
        username=user.username,
        hashed_password=password,
        createdAt = datetime.now(),
        updatedAt = datetime.now(),
        role=user.role
    )
    if user.email:
        db_user.email = user.email
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return(db_user)

def login_user(db: Session, user: schema.UserLogin):
    db_pass = db.query(models.User).filter(models.User.username == user.username).first()
    check = check_password(user.password,db_pass.hashed_password)
    if check:
        return True
    return False