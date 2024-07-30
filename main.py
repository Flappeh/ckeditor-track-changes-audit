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
from services.statistics.api import router as stats_router
from fastapi_pagination import add_pagination
from utils import scheduled_tasks
from contextlib import asynccontextmanager


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduled_tasks.start_scheduler()
    yield
    scheduled_tasks.scheduler.shutdown()
    
app = FastAPI(lifespan=lifespan)
app.include_router(ckeditor_router, tags=['Ckeditor'], include_in_schema=False)
app.include_router(html_router, tags=['Parser'], include_in_schema=False)
app.include_router(admin_router, tags=['Administration'], include_in_schema=False)
app.include_router(audit_router, tags=['Audit Logs'])
app.include_router(stats_router, tags=['Statistics'])

add_pagination(app)


@app.get('/', include_in_schema=False)
def root():
    return RedirectResponse('/docs', status_code=301)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, use_colors=True)