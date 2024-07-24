from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from utils.middleware import get_db
from utils import models
from . import schema, service

router = APIRouter(
    prefix="/audit"
)

@router.get('/author')
async def get_audit_data_from_authorId(authorId: str,limit:int = 100,  db: service.Session = Depends(get_db)):
    return service.get_audit_from_authorId(authorId=authorId, db=db, limit=limit)
