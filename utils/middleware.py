from .database import engine_audit, engine_ckeditor, SessionLocal
from utils import models


models.CKEditorDB.metadata.create_all(engine_ckeditor)
models.AuditDB.metadata.create_all(engine_audit)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()