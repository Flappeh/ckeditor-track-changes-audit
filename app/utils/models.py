from sqlalchemy import Boolean,Column,Integer, String, DateTime, BLOB, Text
from .database import CKEditorDB,AuditDB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT, BINARY

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
    attributesBlob = Column(BINARY)
    visibilityChangedAtVersion = Column(Integer)
    snapshotDate = Column(DateTime)


# Audit Suggestion DB

class AuditMetadata(AuditDB):
    __tablename__ = 'audit_metadata'    
    suggestionId = Column(String(50), primary_key=True, index=True)
    documentId = Column(String(50), index=True)
    authorId = Column(String(50))
    requesterId = Column(String(50))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    type = Column(String(60))
        
class AuditData(AuditDB):
    __tablename__ = "audit_data"
    suggestionId = Column(String(50), primary_key=True, index=True)
    data = Column(LONGTEXT)
        
class AuditSynchronization(AuditDB):
    __tablename__ = "audit_synchronization"
    id = Column(Integer,autoincrement=True, primary_key=True, index=True)
    syncType = Column(String(10))
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    totalSuggestions = Column(Integer)
    totalData = Column(Integer)
    
class User(AuditDB):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True)
    email = Column(String(50), unique=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    role=Column(String(10))
