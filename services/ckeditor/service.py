import os
import requests as req
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs
load_dotenv()

BACKEND_URL = os.getenv('CKEDITOR_BACKEND_URL')

def get_document_by_id(id: str):
    url = BACKEND_URL + f'collab/storage/{id}'
    try:
        response = req.get(url=url)
        return response.text
    except:
        print(f'Error retrieving document {id}')
        
def get_suggestions_from_document(id:str):
    url = BACKEND_URL + f'collab/suggestion?id={id}'
    try:
        response = req.get(url)
        data = response.json()
        return data
    except:
        print(f'Error retrieving suggestions for document: {id}')

    