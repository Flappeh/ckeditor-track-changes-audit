from bs4 import BeautifulSoup as bs
from services.ckeditor import service as ckeditor_service
from utils import models
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from services.ckeditor.schema import TrackChanges
from typing import List
from .schema import AuditBase
import json 
results = {}
parsed_data  = []

def get_all_suggestions(db: Session, skip: int = 0, limit: int=100):
    return db.query(models.TrackChangesSuggestion).offset(skip).limit(limit).all()

def get_all_daily_suggestions(db: Session, skip: int = 0, limit: int=100):
    one_day = timedelta(hours=24)
    last_one_day = datetime.now() - one_day
    return db.query(models.TrackChangesSuggestion).filter(models.TrackChangesSuggestion.updatedAt > last_one_day).offset(skip).limit(limit).all()

def get_all_distinct_documents(db: Session,skip:int = 0, limit:int = 100):
    data = db.query(models.TrackChangesSuggestion.documentId).distinct().offset(skip).limit(limit).all()
    return [i[0] for i in data]

def convert_to_audit_base(data: List[TrackChanges]):
    try:
        return [{
            "suggestionId": i.id,
            "authorId": i.authorId,
            "createdAt": i.createdAt,
            "updatedAt": i.updatedAt,
            "type": i.type,
        } for i in data]
    except:
        print("Error converting data")
        
def synchronize_suggestion_data(db: Session):
    try:
        daily_suggestions = ckeditor_service.get_all_daily_suggestions(db=db)
        converted =  convert_to_audit_base(daily_suggestions)
        insert_suggestions_to_db(db, converted)
    except:
        print("Error occured on synchronizing suggestion data")
        
def insert_suggestions_to_db(db: Session, data: List[AuditBase]):
    try:
        print(data)
        objects = [AuditBase(**i) for i in data]
        db.bulk_save_objects(objects=objects)
        db.commit()
        return data
    except: 
        print("Error inserting suggestions")

def process_daily_suggestion(document_id: str):
    pass


def parse_suggestion_from_html(htmlData:str = None):
    soup = bs(htmlData, 'html.parser')
    # Check for text input
    text_suggestions = soup.find_all('suggestion-start')
    for i in text_suggestions:
        current_content = i.next.get_text()
        results[i['name']] = current_content
    # for paragraph in paragraphs:
    #     # Initialize variables to store content and current suggestion name
    #     current_content = []
    #     current_name = None

    #     # Find all text nodes and suggestion tags within the current paragraph
    #     for child in paragraph.children:
    #         if child.name == 'suggestion-start':
    #             current_name = child['name']
    #             current_content = []  # Reset content for new suggestion-start tag
    #         elif child.name == 'suggestion-end' and current_name:
    #             if current_name in results:  # Check if name already exists in results
    #                 results[current_name] += ''.join(current_content).strip()
    #             else:
    #                 results[current_name] = ''.join(current_content).strip()
    #             current_name = None
    #         else:
    #             current_content.append(str(child))

    # #Check for other element input
    # figures = soup.find_all('figure', {"data-suggestion-end-after": True})
    
    # for figure in figures:
    #     current_content = []
    #     current_name = figure['data-suggestion-end-after']
    #     results[current_name] = figure.html
                
    
    # Print results
    for name, content in results.items():
        parsed_name = name.split(':')
        data = {
            "type": parsed_name[0],
            "suggestionId": parsed_name[1],
            "authorId": parsed_name[2],
            "data": content
        }
        parsed_data.append(data)
    return parsed_data