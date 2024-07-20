from sqlalchemy import Boolean,Column,Integer, String, DateTime

from database import Base


class TrackChangesMetadata(Base):
    __tablename__ = 'track_changes_metadata'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    suggestionId = Column(String(50))
    authorId = Column(String(50))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    type = Column(String(20))
    
class TrackChangesData(Base):
    __tablename__ = "track_changes_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    suggestionId = Column(String(50))
    data = Column(String)