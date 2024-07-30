from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from utils.utils import generate_collab_token
from utils.middleware import get_db
from utils import models
from . import schema, service
from utils.exceptions import DatabaseError, DocumentNotFoundError, SuggestionRetrievalError

router = APIRouter(
    prefix="/ckeditor"
)

@router.get('/token')
async def get_ckeditor_token():
    return generate_collab_token()

@router.get('/suggestion', response_model=list[schema.TrackChanges])
async def get_all_suggestions(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    try:
        data = service.get_all_suggestions(db=db, skip=skip, limit=limit)
        return data
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/suggestion/daily', response_model=list[schema.TrackChanges])
async def get_all_daily_suggestions(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    try:
        data = service.get_all_daily_suggestions(db=db, skip=skip, limit=limit)
        return data
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/document-ids')
async def get_all_distinct_document_from_suggestion(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    try:
        return service.get_all_distinct_documents(db=db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/document-ids/daily')
async def get_all_daily_edited_documents(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    try:
        return service.get_all_daily_documents(db=db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/document/{document_id}')
async def get_document(document_id: str):
    try:
        return service.get_document_by_id(document_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get('/document/{document_id}/suggestions')
async def get_document_suggestions(document_id: str):
    try:
        return service.get_suggestions_from_document(document_id)
    except SuggestionRetrievalError as e:
        raise HTTPException(status_code=500, detail=str(e))