from pydantic import BaseModel
from datetime import datetime


class AuditDataResult(BaseModel):
    suggestionId: str
    documentId: str
    authorId: str
    requesterId: str
    createdAt: datetime
    updatedAt: datetime
    type: str
    data: str
    class Config:
        from_orm = True
