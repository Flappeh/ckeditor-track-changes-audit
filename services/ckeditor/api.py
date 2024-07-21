from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from utils.utils import generate_collab_token
from utils.middleware import get_db
from utils import models
from . import schema, service

router = APIRouter(
    prefix="/ckeditor"
)

@router.get('/token')
async def get_ckeditor_token():
    return generate_collab_token()

@router.get('/suggestion', response_model=list[schema.TrackChanges])
async def get_all_suggestions(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    data = service.get_all_suggestions(db=db, skip=skip, limit=limit)
    return data

@router.get('/suggestion/daily', response_model=list[schema.TrackChanges])
async def get_all_daily_suggestions(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    data = service.get_all_daily_suggestions(db=db, skip=skip, limit=limit)
    return data

@router.get('/document-ids')
async def get_all_distinct_document_from_suggestion(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    return service.get_all_distinct_documents(db=db, skip=skip, limit=limit)

@router.get('/document-ids/daily')
async def get_all_daily_edited_documents(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    return service.get_all_daily_documents(db=db, skip=skip, limit=limit)