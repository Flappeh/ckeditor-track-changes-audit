from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from utils.utils import generate_collab_token
from utils.middleware import get_db
from . import schema, service

router = APIRouter(
    prefix="/admin"
)

@router.get('/token')
async def get_ckeditor_token():
    return generate_collab_token()

@router.post('/user', response_model=schema.User)
def create_user(user: schema.UserCreate, db: service.Session = Depends(get_db)):
    db_user = service.get_user_by_username(db,user.username)
    if db_user:
        raise HTTPException(status_code=400, detail=f"User with username {user.username} already registered")
    return service.create_user(db, user)

@router.post('/login')
def login_user(user:schema.UserLogin, db: service.Session = Depends(get_db)):
    db_user = service.login_user(db, user)
    if db_user:
        return {"welcome": user}
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username of password")