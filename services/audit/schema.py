from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from fastapi import Query
class AuditDataResult(BaseModel):
    suggestionId: str = Field(examples=['example-suggestion-id'])
    documentId: str
    authorId: str
    requesterId: str
    createdAt: datetime
    updatedAt: datetime
    type: str
    data: str
    class Config:
        from_orm = True

class OrderBy(str, Enum):
    asc = 'ASC'
    desc = 'DESC'

class AuthorIdParams:
    def __init__(
        self,
    authorId: str = Query(..., description='User Id to search'),
    order: OrderBy = Query('DESC', description='Order of returned results')
    ):
        self.authorId: str = authorId
        self.order: OrderBy = order
        