from fastapi import HTTPException

class DatabaseError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class ConversionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class SynchronizationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class ParsingError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)