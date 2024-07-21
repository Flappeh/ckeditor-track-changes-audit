from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from utils.middleware import get_db
from utils import models
from . import schema, service

router = APIRouter(
    prefix="/audit"
)

@router.get(
    '/suggestion/sync'
    # , response_model=list[schema.AuditBase]
    )
async def synchronize_daily_suggestion(db: service.Session = Depends(get_db)):
    data = service.synchronize_suggestion_data(db=db)
    return data

@router.get('/document-ids')
async def get_all_distinct_document_from_suggestion(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    return service.get_all_distinct_documents(db=db, skip=skip, limit=limit)

@router.get('/document-ids/daily')
async def get_all_daily_edited_documents(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    return service.get_all_daily_documents(db=db, skip=skip, limit=limit)