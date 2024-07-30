from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from fastapi import Query
class AuditDataResult(BaseModel):
    suggestionId: str = Field(examples=['suggestion-id-example'])
    documentId: str = Field(examples=['document-id-example'])
    authorId: str = Field(examples=['author-id'])
    requesterId: str = Field(examples=['requestor-id'])
    createdAt: datetime 
    updatedAt: datetime
    type: str = Field(examples=['insertion','deletion'])
    data: str = Field(examples=['this is the data'])
    class Config:
        from_orm = True

class OrderBy(str, Enum):
    ASC = 'asc'
    DESC = 'desc'

class SortBy(str, Enum):
    createdAt = 'created_at'
    updatedAt = 'updated_at'

class AuthorIdParams:
    def __init__(
        self,
    authorId: str = Query(..., description='User Id to search'),
    order: OrderBy = Query(OrderBy.ASC, description='Order of returned results'),
    sort_by: SortBy = Query(SortBy.createdAt, description='Date to sory by.', example='updated_at')
    ):
        self.authorId: str = authorId
        self.order: OrderBy = order.name
        self.sort_by: SortBy = sort_by.name
        

class TimeRangeParams:
    def __init__(
        self,
    start: str = Query(..., description='Start date to search',example=datetime(2000,1,1)),
    end: str = Query(..., description='End date to search',example=datetime(2000,2,1)),
    order: OrderBy = Query(OrderBy.ASC, description='Order of returned results'),
    sort_by: SortBy = Query(SortBy.createdAt, description='Date to sory by.', example='updated_at')
    ):
        self.start: str = start
        self.end: str = end
        self.order: OrderBy = order.name
        self.sort_by: SortBy = sort_by.name
        

class DocumentIdParams:
    def __init__(
        self,
    documentId: str = Query(..., description='Document Id',example='document-id'),
    order: OrderBy = Query(OrderBy.ASC, description='Order of returned results'),
    sort_by: SortBy = Query(SortBy.createdAt, description='Date to sory by.', example='updated_at')
    ):
        self.documentId: str = documentId
        self.order: OrderBy = order.name
        self.sort_by: SortBy = sort_by.name
        