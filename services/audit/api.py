from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from utils.middleware import get_db
from . import schema, service
from fastapi_pagination import Page

router = APIRouter(
    prefix="/audit"
)

@router.get(path='/author',
            description='Get suggestions from user id',
            )
async def get_audit_data_from_authorId(
    params: schema.AuthorIdParams = Depends(),
    db: service.Session = Depends(get_db)
    ) -> Page[schema.AuditDataResult]:
    data = service.get_audit_from_authorId(authorId=params.authorId, 
                                           order=params.order,
                                           db=db
                                           )
    return data

@router.get(path='/time',
            description='Get suggestions from time range',
            )
async def get_audit_data_from_time_range(
    params: schema.AuthorIdParams = Depends(),
    db: service.Session = Depends(get_db)
    ) -> Page[schema.AuditDataResult]:
    data = service.get_audit_from_authorId(authorId=params.authorId, 
                                           order=params.order,
                                           db=db
                                           )
    return data

