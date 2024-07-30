from utils import models
from sqlalchemy.orm import Session
from datetime import datetime
from . import schema
from sqlalchemy.sql import text
from utils.database import engine_audit
from typing import Optional, List
from fastapi import HTTPException, status
from fastapi_pagination import  paginate
# from fastapi_pagination.ext.sqlalchemy import
import sched

def parse_parameter(authorId:Optional[str], db: Session):
    if authorId:
        user = db.query(models.AuditMetadata).filter(models.AuditMetadata.requesterId == authorId).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id : {authorId} not found!')

def get_audit_from_authorId(authorId:str,order: str,sort_by:str, db:Session) :
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
    # return data
    data = convert_to_audit_format(data)
    return paginate(data)

def get_audit_data_from_time_range(start:datetime, end:datetime, order: str, sort_by: str, db:Session) :
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
    # return data
    data = convert_to_audit_format(data)
    return paginate(data)

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