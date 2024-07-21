from sqlalchemy import Boolean,Column,Integer, String, DateTime, BLOB, Text
from .database import CKEditorDB,AuditDB

# CKEditor Suggestion Table

class TrackChangesSuggestion(CKEditorDB):
    __tablename__ = 'track_changes__suggestion'
    id = Column(String(36), primary_key=True)
    environmentId = Column(String(20), nullable=True)
    authorId = Column(String(96), nullable=True)
    documentId = Column(String(60), nullable=True)
    type = Column(String(60), nullable=True)
    data = Column(Text, nullable=True)
    createdAt = Column(DateTime, nullable=True)
    updatedAt = Column(DateTime, nullable=True)
    deletedAt = Column(DateTime, nullable=True)
    requesterId = Column(String(96), nullable=True)
    originalSuggestionId = Column(String(36), nullable=True)
    hasComments = Column(Integer, nullable=True)
    state = Column(String(8), nullable=True)


# Audit Suggestion DB

class TrackChangesMetadata(AuditDB):
    __tablename__ = 'track_changes_metadata'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    suggestionId = Column(String(50))
    authorId = Column(String(50))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    type = Column(String(20))
    
class TrackChangesData(AuditDB):
    __tablename__ = "track_changes_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    suggestionId = Column(String(50))
    data = Column(Text)