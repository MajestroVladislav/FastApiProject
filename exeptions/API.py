from fastapi import HTTPException

class APIException(HTTPException):
    """Base class for API exceptions."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)