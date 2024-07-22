from fastapi import HTTPException

class DatabaseError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class DocumentNotFoundError(HTTPException):
    def __init__(self, document_id: str):
        super().__init__(status_code=404, detail=f"Document with id {document_id} not found")

class SuggestionRetrievalError(HTTPException):
    def __init__(self, document_id: str):
        super().__init__(status_code=500, detail=f"Error retrieving suggestions for document: {document_id}")