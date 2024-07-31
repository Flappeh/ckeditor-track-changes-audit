from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from utils.middleware import get_db
from . import schema, service
from fastapi_pagination import Page

router = APIRouter(
    prefix="/stats"
)

@router.get(path='/suggestion',
            description='Get total suggestion count from database',
            )
async def get_suggestion_count_from_database(
    db: service.Session = Depends(get_db)
    ):
    try:
        data = service.get_suggestion_count(db=db)
        return data
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
