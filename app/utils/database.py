from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import as_declarative
from urllib.parse import quote_plus
from . import environment as env

@as_declarative()
class CKEditorDB:
    pass

@as_declarative()
class AuditDB:
    pass

engine_ckeditor = create_engine(f"mysql+pymysql://{env.CKEDITOR_DATABASE_USERNAME}:{quote_plus(env.CKEDITOR_DATABASE_PASSWORD)}@{env.CKEDITOR_DATABASE_HOST}/{env.CKEDITOR_DATABASE_NAME}")
engine_audit = create_engine(f"mysql+pymysql://{env.AUDIT_DATABASE_USERNAME}:{quote_plus(env.AUDIT_DATABASE_PASSWORD)}@{env.AUDIT_DATABASE_HOST}/{env.AUDIT_DATABASE_NAME}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
SessionLocal.configure(binds= {
    CKEditorDB: engine_ckeditor,
    AuditDB: engine_audit
})

# Base = declarative_base()
