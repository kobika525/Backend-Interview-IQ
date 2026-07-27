from pathlib import Path
import secrets
from app.config import settings
class StorageService:
 @staticmethod
 def save_bytes(folder:str,original_name:str,data:bytes)->str:
  ext=Path(original_name).suffix.lower(); key=f'{folder}/{secrets.token_hex(16)}{ext}'; path=Path(settings.UPLOAD_DIR)/key; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data); return key
 @staticmethod
 def path(key:str)->Path:
  base=Path(settings.UPLOAD_DIR).resolve(); p=(base/key).resolve()
  if base not in p.parents: raise ValueError('Unsafe storage key')
  return p
