from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env',case_sensitive=False,extra='ignore')
    APP_NAME:str='Interview IQ'; APP_ENV:str='development'; DEBUG:bool=True; API_V1_PREFIX:str='/api'
    SECRET_KEY:str='change-me'; JWT_ALGORITHM:str='HS256'; ACCESS_TOKEN_EXPIRE_MINUTES:int=30; REFRESH_TOKEN_EXPIRE_DAYS:int=7
    DATABASE_URL:str='mysql+pymysql://root:password@localhost:3306/interview_iq'; TEST_DATABASE_URL:str='sqlite:///./test.db'
    FRONTEND_URL:str='http://localhost:5173'; CORS_ORIGINS:str='http://localhost:5173'
    UPLOAD_DIR:str='uploads'; MAX_RESUME_SIZE_MB:int=10; MAX_AUDIO_SIZE_MB:int=50; MAX_VIDEO_SIZE_MB:int=250
    AI_MODE:str='local'; OLLAMA_BASE_URL:str='http://localhost:11434'; OLLAMA_MODEL:str='llama3.2'; OLLAMA_TIMEOUT_SECONDS:int=120
    WHISPER_MODEL:str='base'; SENTENCE_TRANSFORMER_MODEL:str='all-MiniLM-L6-v2'; SPACY_MODEL:str='en_core_web_sm'; FFMPEG_PATH:str='ffmpeg'
    SMTP_HOST:str=''; SMTP_PORT:int=587; SMTP_USERNAME:str=''; SMTP_PASSWORD:str=''; SMTP_FROM_EMAIL:str='noreply@interviewiq.local'
    RATE_LIMIT_ENABLED:bool=False; LOG_LEVEL:str='INFO'; ADMIN_EMAIL:str='admin@interviewiq.com'; ADMIN_PASSWORD:str=''
    @property
    def cors_origins(self): return [x.strip() for x in self.CORS_ORIGINS.split(',') if x.strip()]
@lru_cache
def get_settings(): return Settings()
settings=get_settings()
