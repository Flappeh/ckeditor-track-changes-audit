import requests as req
from utils.environment import BACKEND_URL
from utils import models
from sqlalchemy.orm import Session

def get_all_suggestions(db: Session, skip: int = 0, limit: int=100):
    return db.query(models.TrackChangesSuggestion).offset(skip).limit(limit).all()

def get_all_distinct_documents(db: Session,skip:int, limit:int = 100):
    return db.query(models.TrackChangesSuggestion.documentId).distinct()

def get_document_by_id(id: str):
    url = BACKEND_URL + f'collab/storage/{id}'
    try:
        response = req.get(url=url)
        return response.text
    except:
        print(f'Error retrieving document {id}')
        
def get_suggestions_from_document(id:str):
    url = BACKEND_URL + f'collab/suggestion?id={id}'
    try:
        response = req.get(url)
        data = response.json()
        return data
    except:
        print(f'Error retrieving suggestions for document: {id}')

