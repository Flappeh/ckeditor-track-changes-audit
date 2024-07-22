import logging
from bs4 import BeautifulSoup as bs
from services.ckeditor import service as ckeditor_service
from utils import models
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from services.ckeditor.schema import TrackChanges
from typing import List
from .schema import AuditBase
from .exceptions import DatabaseError, ConversionError, SynchronizationError, ParsingError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.mysql import insert

logger = logging.getLogger(__name__)

results = {}
parsed_data = []


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

def get_all_distinct_documents(db: Session,skip:int = 0, limit:int = 100):
    try:
        data = db.query(models.TrackChangesSuggestion.documentId).distinct().offset(skip).limit(limit).all()
        return [i[0] for i in data]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving distinct documents: {str(e)}")
        raise DatabaseError(f"Error retrieving distinct documents: {str(e)}")

def convert_to_audit_base(data: List[TrackChanges]) -> List[AuditBase]:
    try:
        return [{
            "suggestionId": i.id,
            "documentId": i.documentId,
            "authorId": i.authorId,
            "createdAt": i.createdAt,
            "updatedAt": i.updatedAt,
            "type": i.type,
        } for i in data]
    except Exception as e:
        logger.error(f"Error converting data: {str(e)}")
        raise ConversionError(f"Error converting data: {str(e)}")

def synchronize_all_suggestion_data(db: Session):
    try:
        res = db.query(models.TrackChangesSuggestion).all()
        converted = convert_to_audit_base(res)
        insert_suggestions_to_db(db, converted)
        process_and_insert_audit_data(db)
        return db.query(models.TrackChangesMetadata).all()
    except Exception as e:
        logger.error(f"Error synchronizing all suggestion data: {str(e)}")
        raise SynchronizationError(f"Error synchronizing all suggestion data: {str(e)}")
    
def process_and_insert_audit_data(db: Session):
    try:
        distinct_docs = db.query(models.TrackChangesSuggestion.documentId).distinct().all()
        unique_document_ids = [doc.documentId for doc in distinct_docs]
        
        audit_data_to_insert = []

        for doc_id in unique_document_ids:
            try:
                parsed_data = parse_html_document(doc_id)
                
                for item in parsed_data:
                    audit_data = models.TrackChangesData(
                        suggestionId=item['suggestionId'],
                        data=item['data']
                    )
                    audit_data_to_insert.append(audit_data)
            
            except ParsingError as e:
                logger.error(f"Error parsing document {doc_id}: {str(e)}")
                continue

        db.bulk_save_objects(audit_data_to_insert)
        db.commit()

        logger.info(f"Processed {len(unique_document_ids)} documents and inserted {len(audit_data_to_insert)} audit records.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing and inserting audit data: {str(e)}")
        raise DatabaseError(f"Error processing and inserting audit data: {str(e)}")

def synchronize_suggestion_data(db: Session):
    try:
        daily_suggestions = ckeditor_service.get_all_daily_suggestions(db=db)
        converted = convert_to_audit_base(daily_suggestions)
        insert_suggestions_to_db(db, converted)
    except Exception as e:
        logger.error(f"Error synchronizing suggestion data: {str(e)}")
        raise SynchronizationError(f"Error synchronizing suggestion data: {str(e)}")

def insert_suggestions_to_db(db: Session, data: List[AuditBase]):
    # insert_stmt = insert("audit_metadata").values(
    # id='sugestionId',
    # data='inserted value')
    # on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
    #     data=insert_stmt.values.data,
    #     status='U'
    # )
    try:
        
        objects = [models.TrackChangesMetadata(**i) for i in data]
        db.execute(objects=objects)
        db.commit()
        return data
    except SQLAlchemyError as e:
        logger.error(f"Error inserting suggestions: {str(e)}")
        raise DatabaseError(f"Error inserting suggestions: {str(e)}")

def parse_html_document(id: str):
    try:
        data = ckeditor_service.get_document_by_id(id)
        return parse_suggestion_from_html(data)
    except Exception as e:
        logger.error(f"Error parsing HTML document: {str(e)}")
        raise ParsingError(f"Error parsing HTML document: {str(e)}")

def parse_suggestion_from_html(htmlData:str = None):
    try:
        soup = bs(htmlData, 'html.parser')
        # Check for text input
        text_suggestions = soup.find_all('suggestion-start')
        for i in text_suggestions:
            current_content = i.next.get_text()
            results[i['name']] = current_content
        # #Check for other element input
        figures = soup.find_all('figure', {"data-suggestion-end-after": True})
        print(figures)
        for figure in figures:
            current_content = []
            current_name = figure['data-suggestion-end-after']
            results[current_name] = figure.encode_contents()
                    
        
        # Print results
        for name, content in results.items():
            parsed_name = name.split(':')
            data = {
                "type": parsed_name[0],
                "suggestionId": parsed_name[1],
                "authorId": parsed_name[2],
                "data": content
            }
            parsed_data.append(data)
        return parsed_data
    except Exception as e:
        logger.error(f"Error parsing suggestion from HTML: {str(e)}")
        raise ParsingError(f"Error parsing suggestion from HTML: {str(e)}")