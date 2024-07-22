from dotenv import load_dotenv
from services.ckeditor import service as ckeditor
from services.htmlparse.service import parse_suggestion_from_html as parse_html
from fastapi import FastAPI, HTTPException, Depends, status
import uvicorn
from services.ckeditor.api import router as ckeditor_router
from services.htmlparse.api import router as html_router
from services.admin.api import router as admin_router
load_dotenv()

app = FastAPI()
app.include_router(ckeditor_router)
app.include_router(html_router)
app.include_router(admin_router)

@app.get('/')
def root():
    return ("Hello my guy")

@app.get('/{id}')
def get_ckeditor_document(id: str):
    data = ckeditor.get_document_by_id(id)
    res = parse_html(data)
    return res

# def main():
#     data = ckeditor.get_document_by_id('demo-doc-1')
#     result = parse_html(data)
#     data = json.dumps(result)
#     print(data)
    
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)