import json
import logging
from bs4 import BeautifulSoup as bs
from bs4.element import NavigableString, Tag, ResultSet
from services.ckeditor import service as ckeditor_service
from utils import models
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from services.ckeditor.schema import TrackChanges
from typing import List
from .schema import AuditMetadata, AuditData
from .exceptions import DatabaseError, ConversionError, SynchronizationError, ParsingError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.mysql import insert
from typing import Any
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

def get_all_distinct_documents(db: Session,skip:int = 0, limit:int = 100):
    try:
        data = db.query(models.TrackChangesSuggestion.documentId).distinct().offset(skip).limit(limit).all()
        return [i[0] for i in data]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving distinct documents: {str(e)}")
        raise DatabaseError(f"Error retrieving distinct documents: {str(e)}")

def convert_to_audit_base(data: List[TrackChanges]) -> List[models.AuditMetadata]:
    try:
        return [{
            "suggestionId": i.id,
            "documentId": i.documentId,
            "authorId": i.authorId,
            "requesterId": i.requesterId,
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
        all_metadatas = insert_suggestions_to_db(db, converted)
        inserted = process_and_insert_audit_data(db, all_metadatas)
        return inserted
    except Exception as e:
        logger.error(f"Error synchronizing all suggestion data: {str(e)}")
        raise SynchronizationError(f"Error synchronizing all suggestion data: {str(e)}")
    
def process_and_insert_audit_data(db: Session, documentIds: List[AuditMetadata]):
    try:
        document_id_list = [i['documentId'] for i in documentIds]
        unique_document_ids = list(dict.fromkeys(document_id_list))
        audit_data_to_insert = []
        for doc_id in unique_document_ids:
            try:
                parsed_data = parse_html_document(doc_id)
                audit_data_to_insert.extend(parsed_data)
            except ParsingError as e:
                logger.error(f"Error parsing document {doc_id}: {str(e)}")
                continue
        stmt = insert(models.AuditData).values(audit_data_to_insert)
        stmt = stmt.on_duplicate_key_update(
            data=stmt.inserted.data
            )
        db.execute(stmt)
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
        all_metadata = insert_suggestions_to_db(db, converted)
        process_and_insert_audit_data(db, all_metadata)
    except Exception as e:
        logger.error(f"Error synchronizing suggestion data: {str(e)}")
        raise SynchronizationError(f"Error synchronizing suggestion data: {str(e)}")

def insert_suggestions_to_db(db: Session, data: List[AuditMetadata]):
    try:
        stmt = insert(models.AuditMetadata).values(data)
        stmt = stmt.on_duplicate_key_update(
            requesterId=stmt.inserted.requesterId, 
            updatedAt=stmt.inserted.updatedAt
            )
        db.execute(stmt)
        db.commit()
        return data
    except SQLAlchemyError as e:
        logger.error(f"Error inserting suggestions: {str(e)}")
        raise DatabaseError(f"Error inserting suggestions: {str(e)}")

def parse_html_document(id: str) -> List[models.AuditData]:
    try:
        print(id)
        data = ckeditor_service.get_document_by_id(id)
        return parse_suggestion_from_html(data)
    except Exception as e:
        logger.error(f"Error parsing HTML document: {str(e)}")
        raise ParsingError(f"Error parsing HTML document: {str(e)}")

def parse_suggestion_from_html(htmlData:str = None) -> List[models.AuditData]:
    try:
        results = {}
        parsed_data = []
        soup = bs(htmlData, 'html.parser')

        # Check for text input with "suggestion-start" attribute
        text_suggestions = soup.find_all('suggestion-start')
        # Check for other text input with "data-suggestion-end-after" attribute
        other_text_suggestions = soup.find_all('p', {"data-suggestion-start-before": True})
        results.update(parse_text_from_html('name',text_suggestions)) if text_suggestions.__len__() != 0 else None
        results.update(parse_text_from_html("data-suggestion-start-before",other_text_suggestions)) if other_text_suggestions.__len__() != 0 else None


        # #Check for other element input
        figures = soup.find_all("figure",{"data-suggestion-end-after": True})
        for figure in figures:
            current_name = figure['data-suggestion-end-after']
            results[current_name] = figure.encode_contents()

        
        # # Print results
        for name, content in results.items():
            parsed_name = name.split(':')
            data = {
                # "type": parsed_name[0],
                "suggestionId": parsed_name[1],
                # "authorId": parsed_name[2],
                "data": content
            }
            parsed_data.append(data)
        return parsed_data
    except Exception as e:
        logger.error(f"Error parsing suggestion from HTML: {str(e)}")
        raise ParsingError(f"Error parsing suggestion from HTML: {str(e)}")
    

def parse_text_from_html(tagName: str, data: ResultSet[Any]) -> dict:
    current_content = []
    results = {}
    for i in data:
        current_element = i
        next_element = i.next
        while True:
            if type(next_element) == Tag and (next_element.name == 'suggestion-end' or 'data-suggestion-end-after' in next_element.attrs):
                break
            elif type(next_element) == NavigableString:
                current_content.append(next_element)
            current_element = next_element
            next_element = current_element.next
        results[i[tagName]] = ''.join(current_content)
    return results