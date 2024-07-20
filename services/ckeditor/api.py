from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from utils.utils import generate_collab_token

router = APIRouter(
    prefix="/ckeditor"
)

@router.get('/token')
async def get_ckeditor_token():
    return generate_collab_token()