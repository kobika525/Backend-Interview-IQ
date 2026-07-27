from datetime import datetime,timedelta,timezone
import hashlib,secrets,uuid
from jose import jwt,JWTError
from pwdlib import PasswordHash
from app.config import settings
password_hasher=PasswordHash.recommended()
def hash_password(password:str)->str:return password_hasher.hash(password)
def verify_password(password:str,hashed:str)->bool:
 try:return password_hasher.verify(password,hashed)
 except Exception:return False
def create_access_token(user_id:int,role:str)->tuple[str,int]:
 exp=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
 return jwt.encode({'sub':str(user_id),'role':role,'type':'access','exp':exp},settings.SECRET_KEY,algorithm=settings.JWT_ALGORITHM),settings.ACCESS_TOKEN_EXPIRE_MINUTES*60
def decode_access_token(token:str)->dict:
 try:
  p=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
  if p.get('type')!='access': raise ValueError('Invalid token type')
  return p
 except (JWTError,ValueError) as e: raise ValueError('Invalid or expired token') from e
def new_opaque_token()->str:return secrets.token_urlsafe(48)
def token_hash(token:str)->str:return hashlib.sha256(token.encode()).hexdigest()
def new_family_id()->str:return str(uuid.uuid4())
