from pydantic import BaseModel, Field
from datetime import datetime


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
