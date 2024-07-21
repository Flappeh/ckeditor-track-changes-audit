from pydantic import BaseModel
from datetime import datetime


class AuditBase(BaseModel):
    suggestionId: str
    authorId: str
    createdAt: datetime
    updatedAt: datetime
    type: str
    class Config:
        from_orm = True

class AuditDataBase(BaseModel):
    suggestionId: str
    data: str
    class Config:
        from_orm = True
