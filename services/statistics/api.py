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

@router.get(path='/time',
            description='Get suggestions from time range',
            )
async def get_audit_data_from_time_range(
    params: schema.TimeRangeParams = Depends(),
    db: service.Session = Depends(get_db)
    ) -> Page[schema.AuditDataResult]:
    if params.start > params.end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date must be before End date")
    
    try:
        data = service.get_audit_data_from_time_range(
                                            start=params.start,
                                            end=params.end,
                                            sort_by=params.sort_by, 
                                            order=params.order,
                                            db=db
                                            )
        return data
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e)

@router.get(path='/document',
            description='Get suggestions from document id',
            )
async def get_audit_data_from_document_id(
    params: schema.DocumentIdParams = Depends(),
    db: service.Session = Depends(get_db)
    ) -> Page[schema.AuditDataResult]:
    try:
        data = service.get_audit_data_from_time_range(
                                            documentId=params.documentId,
                                            sort_by=params.sort_by, 
                                            order=params.order,
                                            db=db
                                            )
        return data
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e)

