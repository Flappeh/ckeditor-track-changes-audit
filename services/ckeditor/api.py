from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from utils.utils import generate_collab_token
from utils.database import engine,SessionLocal
from utils import models
from . import schema, service

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/ckeditor"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/token')
async def get_ckeditor_token():
    return generate_collab_token()

@router.get('/suggestion', response_model=list[schema.TrackChanges])
async def get_all_suggestions(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    data = service.get_all_suggestions(db=db, skip=skip, limit=limit)
    return data

@router.get('/document-ids')
async def get_all_distinct_document_from_suggestion(skip: int = 0, limit:int = 100, db: service.Session = Depends(get_db)):
    data = service.get_all_distinct_documents(db=db, skip=skip, limit=limit)