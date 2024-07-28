import requests as req
import logging
from utils.environment import BACKEND_URL
from utils import models
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError
from utils.exceptions import DatabaseError, DocumentNotFoundError, SuggestionRetrievalError

logger = logging.getLogger(__name__)

def get_all_suggestions(db: Session, skip: int = 0, limit: int=100):
    try:
        return db.query(models.TrackChangesSuggestion).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving suggestions: {str(e)}")
        raise DatabaseError(f"Error retrieving suggestions: {str(e)}")

def get_all_daily_suggestions(db: Session, skip: int = 0, limit: int=100):
    try:
        one_day = timedelta(hours=24)
        last_one_day = datetime.now() - one_day
        return db.query(models.TrackChangesSuggestion).filter(models.TrackChangesSuggestion.updatedAt > last_one_day).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving daily suggestions: {str(e)}")
        raise DatabaseError(f"Error retrieving daily suggestions: {str(e)}")

def get_all_distinct_documents(db: Session, skip:int = 0, limit:int = 100):
    try:
        data = db.query(models.TrackChangesSuggestion.documentId).distinct().offset(skip).limit(limit).all()
        return [i[0] for i in data]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving distinct documents: {str(e)}")
        raise DatabaseError(f"Error retrieving distinct documents: {str(e)}")

def get_all_daily_documents(db:Session, skip:int = 0, limit: int = 100 ):
    try:
        one_day = timedelta(hours=24)
        last_one_day = datetime.now() - one_day
        data = db.query(models.TrackChangesSuggestion.documentId).filter(models.TrackChangesSuggestion.updatedAt > last_one_day).distinct().offset(skip).limit(limit).all()
        return [i[0] for i in data]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving daily documents: {str(e)}")
        raise DatabaseError(f"Error retrieving daily documents: {str(e)}")

def get_document_by_id(id: str):
    url = BACKEND_URL + f'collab/storage/{id}'
    try:
        response = req.get(url=url)
        response.raise_for_status()
        return response.text
    except req.RequestException as e:
        logger.error(f"Error retrieving document {id}: {str(e)}")
        raise DocumentNotFoundError(id)

def get_suggestions_from_document(id:str):
    url = BACKEND_URL + f'collab/suggestion?id={id}'
    try:
        response = req.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except req.RequestException as e:
        logger.error(f"Error retrieving suggestions for document {id}: {str(e)}")
        raise SuggestionRetrievalError(id)