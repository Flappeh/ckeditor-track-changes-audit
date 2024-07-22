from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from utils.middleware import get_db
from utils import models
from . import schema, service
from .exceptions import DatabaseError, ConversionError, SynchronizationError, ParsingError

router = APIRouter(
    prefix="/audit"
)

@router.put('/suggestion/sync')
async def synchronize_daily_suggestion(db: service.Session = Depends(get_db)):
    try:
        data = service.synchronize_suggestion_data(db=db)
        return data
    except SynchronizationError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.put('/suggestion/sync-all')
async def synchronize_all_suggestions(db: service.Session = Depends(get_db)):
    try:
        data = service.synchronize_all_suggestion_data(db=db)
        return data
    except SynchronizationError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.get('/document-ids')
async def get_all_distinct_document_from_suggestion(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    try:
        return service.get_all_distinct_documents(db=db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.get('/document-ids/daily')
async def get_all_daily_edited_documents(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    try:
        return service.get_all_daily_documents(db=db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.get('/parse/{id}')
async def parse_document_suggestions_from_id(id: str=None):
    try:
        return service.parse_html_document(id)
    except ParsingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))