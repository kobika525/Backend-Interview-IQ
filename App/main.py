from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.api.router import api_router
from app.core.exceptions import AppError,app_error_handler,validation_handler,unexpected_handler
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
app=FastAPI(title=settings.APP_NAME,version='1.0.0',docs_url='/docs',redoc_url='/redoc')
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.add_middleware(RequestIDMiddleware); app.add_middleware(SecurityHeadersMiddleware)
app.add_exception_handler(AppError,app_error_handler); app.add_exception_handler(RequestValidationError,validation_handler); app.add_exception_handler(Exception,unexpected_handler)
app.include_router(api_router,prefix=settings.API_V1_PREFIX)
@app.get('/health')
def health(): return {'status':'ok','service':settings.APP_NAME}
@app.get('/api/health')
def api_health(): return {'success':True,'data':{'status':'ok'}}
@app.get('/api/ready')
def ready(): return {'success':True,'data':{'status':'ready'}}
