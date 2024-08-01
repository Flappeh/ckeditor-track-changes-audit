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
from sqlalchemy import update
from utils.utils import get_logger

logger = get_logger()


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
        sync = start_new_synchronization(db, 'all')
        res = db.query(models.TrackChangesSuggestion).all()
        converted = convert_to_audit_base(res)
        all_metadata = insert_suggestions_to_db(db, converted)
        inserted = process_and_insert_audit_data(db, all_metadata)
        update_synchronization(db, sync, len(all_metadata), inserted)
    except Exception as e:
        logger.error(f"Error synchronizing all suggestion data: {str(e)}")
        raise SynchronizationError(f"Error synchronizing all suggestion data: {str(e)}")

def sync_all_metadata(db: Session):
    try:
        sync = start_new_synchronization(db=db, type='metadata')
        res = db.query(models.TrackChangesSuggestion).all()
        if len(res) <= 0:
            update_synchronization(db, sync, 0, 0)
            return
        converted = convert_to_audit_base(res)
        all_metadata = insert_suggestions_to_db(db, converted)
        return (f"Finished synchronizing {len(all_metadata)} metadata")
    except Exception as e:
        logger.error(f"Error synchronizing suggestion data: {str(e)}")
        raise SynchronizationError(f"Error synchronizing suggestion data: {str(e)}")

def synchronize_daily_suggestion_data(db: Session):
    try:
        sync = start_new_synchronization(db=db, type='daily')
        one_day = timedelta(hours=24)
        last_one_day = datetime.now() - one_day
        daily_suggestions = db.query(models.TrackChangesSuggestion).filter(models.TrackChangesSuggestion.createdAt > last_one_day).all()
        if len(daily_suggestions) <= 0:
            update_synchronization(db, sync, 0, 0)
            return
        converted = convert_to_audit_base(daily_suggestions)
        all_metadata = insert_suggestions_to_db(db, converted)
        inserted = process_and_insert_audit_data(db, all_metadata)
        update_synchronization(db, sync, len(all_metadata), inserted)
    except Exception as e:
        logger.error(f"Error synchronizing suggestion data: {str(e)}")
        raise SynchronizationError(f"Error synchronizing suggestion data: {str(e)}")

def update_synchronization(db:Session, sync_item: models.AuditSynchronization, total_metadata, total_data):
    try:
        sync_item.endTime = datetime.now()
        sync_item.totalData = total_data
        sync_item.totalSuggestions = total_metadata
        db.commit()
        db.refresh(sync_item)
    except Exception:
        raise DatabaseError('Error updating synchronization')

def start_new_synchronization(db:Session, type:str):
    logger.info(f'Received synchronization request, type: {type}')
    new_sync = models.AuditSynchronization(
        syncType= type,
        startTime = datetime.now()
    )
    db.add(new_sync)
    db.commit()
    db.refresh(new_sync)
    return new_sync

def check_running_synchronization(db: Session):
    error = None
    try:
        res = db.query(models.AuditSynchronization).order_by(models.AuditSynchronization.startTime.desc()).first()
        if res and res.endTime == None:
            error = SynchronizationError('Synchronization already running')
            logger.error('Received synchronization request while synchronization already running')
            raise error
    except Exception:
        raise error

def delete_running_synchronization(db: Session):
    try:
        res = db.query(
            models.AuditSynchronization
            ).order_by(
                models.AuditSynchronization.startTime.desc()
                ).filter(models.AuditSynchronization.endTime == None
                         ).first()
        if res and res.endTime == None:
            db.delete(res)
            logger.error('Removed running synchronization')
            return {"Message": "Removed running synchronization"}
    except Exception:
        raise DatabaseError('Error deleting synchronization data')
    
def process_and_insert_audit_data(db: Session, documentIds: List[AuditMetadata]):
    try:
        document_id_list = [i['documentId'] for i in documentIds]
        unique_document_ids = list(dict.fromkeys(document_id_list))
        inserted_data = 0
        for doc_id in unique_document_ids:
            try:
                parsed_data = parse_html_document(doc_id)
                if len(parsed_data) == 0:
                    continue
                insert_auditdata_to_db(db, parsed_data)
                inserted_data += len(parsed_data)
            except ParsingError as e:
                logger.error(f"Error parsing document {doc_id}: {str(e)}")
                continue
            except DatabaseError as e:
                logger.error(f"Error inserting data for document : {doc_id} to database")
                continue
            except Exception as e:
                logger.error(f'Error encountered on document {doc_id}')
                continue
        logger.info(f"Processed {len(unique_document_ids)} documents and inserted {inserted_data} audit records.")
        return inserted_data
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing and inserting audit data: {str(e)}")
        raise DatabaseError(f"Error processing and inserting audit data: {str(e)}")

def insert_auditdata_to_db(db:Session, data: models.AuditData):
    try:
        stmt = insert(models.AuditData).values(data)
        stmt = stmt.on_duplicate_key_update(
            data=stmt.inserted.data
            )
        db.execute(stmt)
        db.commit()
    except Exception as e:
        raise DatabaseError(f"Error inserting data for suggestionId : {data.suggestionId} to database")

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
        data = ckeditor_service.get_document_by_id(id)
        return parse_suggestion_from_html(data)
    except Exception as e:
        logger.error(f"Error parsing HTML document: {str(e)}")
        raise ParsingError(f"Error parsing HTML document: {str(e)}")

def parse_suggestion_from_html(htmlData: str = None) -> List[models.AuditData]:
    try:
        results = {}
        parsed_data = []
        soup = bs(htmlData, 'html.parser')

        # Check for text input with "suggestion-start" attribute
        text_suggestions = soup.find_all('suggestion-start')
        # Check for other text input with "data-suggestion-end-after" attribute
        other_text_suggestions = soup.find_all('p', {"data-suggestion-start-before": True})
        
        if text_suggestions:
            results.update(parse_text_from_html('name', text_suggestions))
        if other_text_suggestions:
            results.update(parse_text_from_html("data-suggestion-start-before", other_text_suggestions))

        # Check for other element input
        figures = soup.find_all(lambda tag: tag.has_attr('data-suggestion-end-after'))
        for figure in figures:
            current_name = figure['data-suggestion-end-after']
            results[current_name] = figure.encode_contents()
            if figure.name == 'img':
                results[current_name] = figure.encode()

        # Process results
        for name, content in results.items():
            parsed_name = name.split(':')
            data = {
                "suggestionId": parsed_name[-2] if len(parsed_name) >= 3 else parsed_name[-1],
                "data": 'Column Table' if ('tableColumn' in name) else content,
            }
            parsed_data.append(data)

        return parsed_data

    except AttributeError as e:
        logger.error(f"AttributeError in parse_suggestion_from_html: {str(e)}")
        raise ParsingError(f"Error accessing attribute while parsing HTML: {str(e)}")
    except KeyError as e:
        logger.error(f"KeyError in parse_suggestion_from_html: {str(e)}")
        raise ParsingError(f"Missing key while parsing HTML: {str(e)}")
    except ValueError as e:
        logger.error(f"ValueError in parse_suggestion_from_html: {str(e)}")
        raise ParsingError(f"Value error while parsing HTML: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in parse_suggestion_from_html: {str(e)}")
        raise ParsingError(f"Unexpected error while parsing HTML: {str(e)}")

def parse_text_from_html(tagName: str, data: ResultSet[Any]) -> dict:
    try:
        current_content = []
        results = {}
        for i in data:
            current_element = i
            next_element = i.next
            while True:
                if type(next_element) == Tag and ((next_element.name == 'suggestion-end'
                                                   and 
                                                   next_element.attrs['name'] == i[tagName]
                                                   ) 
                                                  or 
                                                  'data-suggestion-end-after' in next_element.attrs):
                    results[i[tagName]] = ''.join(current_content)
                    current_content = []
                    break
                elif type(next_element) == NavigableString:
                    current_content.append(next_element)
                current_element = next_element
                next_element = current_element.next
                
                if next_element is None:
                    logger.warning(f"End of document reached without finding suggestion-end for {i[tagName]}")
                    break

        return results

    except AttributeError as e:
        logger.error(f"AttributeError in parse_text_from_html: {str(e)}")
        raise ParsingError(f"Error accessing attribute while parsing HTML: {str(e)}")
    except KeyError as e:
        logger.error(f"KeyError in parse_text_from_html: {str(e)}")
        raise ParsingError(f"Missing key while parsing HTML: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in parse_text_from_html: {str(e)}")
        raise ParsingError(f"Unexpected error while parsing HTML: {str(e)}")