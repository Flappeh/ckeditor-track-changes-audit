from pydantic import BaseModel
from datetime import datetime


class AuditMetadata(BaseModel):
    suggestionId: str
    documentId: str
    authorId: str
    requesterId: str
    createdAt: datetime
    updatedAt: datetime
    type: str
    class Config:
        from_orm = True

class AuditData(BaseModel):
    suggestionId: str
    data: str
    class Config:
        from_orm = True
