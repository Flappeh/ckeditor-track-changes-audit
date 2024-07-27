from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from utils.middleware import get_db
from utils import models
from . import schema, service

router = APIRouter(
    prefix="/audit"
)

@router.get(path='/author',
            response_model=schema.AuditDataResult,
            description='Get suggestions from user id'
            )
async def get_audit_data_from_authorId(authorId: str,skip:int=0, limit:int = 100,order:str="desc",  db: service.Session = Depends(get_db)):
    data = service.get_audit_from_authorId(authorId=authorId, 
                                           db=db, 
                                           limit=limit,
                                           order=order,
                                           skip=skip
                                           )
    return data
