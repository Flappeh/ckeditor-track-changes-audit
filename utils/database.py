from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, as_declarative
from .environment import CKEDITOR_DATABASE_URL, AUDIT_DATABASE_URL

@as_declarative()
class CKEditorDB:
    pass

@as_declarative()
class AuditDB:
    pass

engine_ckeditor = create_engine(CKEDITOR_DATABASE_URL)
engine_audit = create_engine(AUDIT_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
SessionLocal.configure(binds= {
    CKEditorDB: engine_ckeditor,
    AuditDB: engine_audit
})

# Base = declarative_base()
