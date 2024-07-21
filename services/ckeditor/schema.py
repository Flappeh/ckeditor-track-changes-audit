from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrackChanges(BaseModel):
    id:str
    environmentId: Optional[str]
    authorId: Optional[str]
    documentId: Optional[str]
    type: Optional[str]
    data: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    deletedAt: Optional[datetime]
    requesterId: Optional[str]
    originalSuggestionId: Optional[str]
    hasComments: int
    state: Optional[str]
    
    class Config:
        from_orm = True
