from utils import models
from sqlalchemy.orm import Session
from datetime import datetime
from . import schema
from sqlalchemy.sql import text
from utils.database import engine_audit
from typing import Optional, List
from fastapi import HTTPException, status
from fastapi_pagination import  paginate
from utils.utils import get_logger
from utils.exceptions import DatabaseError, UserNotFoundError

from fastapi_pagination.utils import disable_installed_extensions_check

logger = get_logger()
disable_installed_extensions_check()
def parse_parameter(authorId:Optional[str], db: Session):
    if authorId:
        user = db.query(models.AuditMetadata).filter(models.AuditMetadata.requesterId == authorId).first()
        if not user:
            raise UserNotFoundError(f'User with id : {authorId} not found!')

def get_audit_from_authorId(authorId:str,order: str,sort_by:str, db:Session) :
    try:
        parse_parameter(authorId=authorId, db=db)
        query_text = text(
            f"""SELECT * FROM {models.AuditMetadata.__tablename__} a 
                JOIN {models.AuditData.__tablename__} b 
                ON a.suggestionId = b.suggestionId
                WHERE a.authorId = :authorId
                ORDER BY a.{sort_by} {order}
            """
            )
        params = {
            "authorId": authorId
            }
        data = db.execute(query_text,params=params,bind_arguments={"bind": engine_audit})    
        data = convert_to_audit_format(data)
        return paginate(data)
    except UserNotFoundError:
        raise UserNotFoundError(f'User with id : {authorId} not found!')
    except Exception:
        logger.error(f"Error retrieving logs for authorId : {authorId}")
        raise DatabaseError(f"Error retrieving logs for authorId : {authorId}")

def get_audit_from_documentId(documentId:str,order: str,sort_by:str, db:Session) :
    try:
        query_text = text(
            f"""SELECT * FROM {models.AuditMetadata.__tablename__} a 
                JOIN {models.AuditData.__tablename__} b 
                ON a.suggestionId = b.suggestionId
                WHERE a.documentId = :documentId
                ORDER BY a.{sort_by} {order}
            """
            )
        params = {
            "documentId": documentId
            }
        data = db.execute(query_text,params=params,bind_arguments={"bind": engine_audit})    
        data = convert_to_audit_format(data)
        return paginate(data)
    except UserNotFoundError:
        raise UserNotFoundError(f'Document with id : {documentId} not found!')
    except Exception:
        logger.error(f"Error retrieving logs for documentId : {documentId}")
        raise DatabaseError(f"Error retrieving logs for documentId : {documentId}")
    
def get_audit_data_from_time_range(start:datetime, end:datetime, order: str, sort_by: str, db:Session) :
    try:
        query_text = text(
            f"""SELECT * FROM {models.AuditMetadata.__tablename__} a 
                JOIN {models.AuditData.__tablename__} b 
                ON a.suggestionId = b.suggestionId
                WHERE a.updatedAt >= :start
                and a.updatedAt <= :end
                ORDER BY a.{sort_by} {order}
            """
            )
        params = {
            "start" : start,
            "end": end
            }
        data = db.execute(query_text,params=params,bind_arguments={"bind": engine_audit})
        data = convert_to_audit_format(data)
        return paginate(data)
    except Exception as e:
        logger.error(f"Error retrieving logs from given timestamp")
        raise DatabaseError(f"Error retrieving logs from given timestamp")

def convert_to_audit_format(data: list[tuple]) -> List[schema.AuditDataResult]:
    return [{
        "suggestionId": i[0],
        "documentId": i[1],
        "authorId": i[2],
        "requesterId": i[3],
        "createdAt": i[4],
        "updatedAt": i[5],
        "type": i[6],
        "data": i[8]
        } for i in data]