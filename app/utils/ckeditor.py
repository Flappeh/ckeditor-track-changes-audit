from utils.environment import CKEDITOR_COLLAB_ACCESS_KEY, CKEDITOR_COLLAB_API_URL, CKEDITOR_COLLAB_API_SECRET, CKEDITOR_COLLAB_ENV_ID, CKEDITOR_COLLAB_ORG_ID
import requests as req
from utils.utils import generateSignature
from time import time
from utils.exceptions import DocumentNotFoundError
from utils.utils import get_logger

logger = get_logger()

def generate_headers(timestamp, signature):
    return{
            "X-CS-Timestamp" : str(timestamp),
            "X-CS-Signature" : signature
    }

def get_document_from_storage(id: str):
    logger.info(f'Requesting document : {id} to document storage')
    url = CKEDITOR_COLLAB_API_URL + f'storage/{id}'
    timestamp = round(time() * 1000)
    signature = generateSignature(method='GET', timestamp=timestamp,uri=url,body=None)
    try:
        res = req.get(url=url,headers=generate_headers(timestamp,signature))
        res.raise_for_status()
        return res.text
    except req.RequestException as e:
        logger.error(f'Failed requesting document : {id}, message {e.response}')
        raise DocumentNotFoundError(id)
    

def get_suggestions_from_documentId(id: str):
    logger.info(f'Requesting suggestion for document : {id}')
    url = CKEDITOR_COLLAB_API_URL + f'suggestions?document_id={id}&limit=1000&sort_by=updated_at&order=desc'
    timestamp = round(time() * 1000)
    signature = generateSignature(method='GET', timestamp=timestamp,uri=url,body=None)
    try:
        res = req.get(url=url,headers=generate_headers(timestamp,signature))
        res.raise_for_status()
        return res.json()
    except req.RequestException as e:
        logger.error(f'Failed requesting document suggestions for documentId : {id}, message {e.response}')
        raise DocumentNotFoundError(id)
    
    