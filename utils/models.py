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
    __tablename__ = 'audit_metadata'    
    suggestionId = Column(String(50), primary_key=True, index=True)
    documentId = Column(String(50), index=True)
    authorId = Column(String(50))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    type = Column(String(20))
    
class TrackChangesData(AuditDB):
    __tablename__ = "audit_data"
    suggestionId = Column(String(50), primary_key=True, index=True)
    data = Column(Text)
    
class User(AuditDB):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True)
    email = Column(String(50), unique=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    role=Column(String(10))
