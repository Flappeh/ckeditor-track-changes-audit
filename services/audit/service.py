import requests as req
from utils.environment import BACKEND_URL
from utils import models
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from . import schema
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import text
from utils.database import engine_audit
from typing import List,Optional

def parse_parameter(authorId:Optional[str], skip:Optional[int],limit: Optional[int]):
    pass

def get_audit_from_authorId(authorId:str,skip: int, limit:int,order: str, db:Session):
    query_text = text(
        f"""SELECT * FROM audit_metadata a 
            JOIN audit_data b 
            ON a.suggestionId = b.suggestionId
            WHERE a.authorId = :authorId
            ORDER BY a.updatedAt {order}
            LIMIT :limit
            OFFSET :skip
        """
        )
    params = {
        "authorId": authorId, 
        "order": order.upper(),
        "limit": limit,
        "skip": skip
        }
    data = db.execute(query_text,params=params,bind_arguments={"bind": engine_audit})
    data = convert_to_audit_format(data)
    return data

def get_audit_from_date(start:datetime,end:datetime,limit:int, db:Session):
    query_text = text(
        f"""SELECT * FROM audit_metadata a 
            JOIN audit_data b 
            ON a.suggestionId = b.suggestionId
            WHERE a.updatedAt > :start
            AND a.updatedAt < :end
            LIMIT :limit
        """
        )
    data = db.execute(query_text,{"start": start, "end": end, "limit": limit},bind_arguments={"bind": engine_audit})
    data = convert_to_audit_format(data)
    return data

def convert_to_audit_format(data: List[tuple]) -> schema.AuditDataResult:
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