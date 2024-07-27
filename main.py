from dotenv import load_dotenv
from services.ckeditor import service as ckeditor
from services.htmlparse.service import parse_suggestion_from_html as parse_html
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
import uvicorn
from services.ckeditor.api import router as ckeditor_router
from services.htmlparse.api import router as html_router
from services.admin.api import router as admin_router
from services.audit.api import router as audit_router
load_dotenv()

app = FastAPI()
app.include_router(ckeditor_router, tags=['Ckeditor'])
app.include_router(html_router, tags=['Parser'])
app.include_router(admin_router, tags=['Administration'])
app.include_router(audit_router, tags=['Audit'])

@app.get('/', include_in_schema=False)
def root():
    return RedirectResponse('/docs', status_code=301)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, use_colors=True)