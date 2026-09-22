from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent
load_dotenv(BASE_DIR/'.env')
def env_bool(name,default=False):
    v=os.getenv(name)
    return default if v is None else v.strip().lower() in {'1','true','yes','si','sí','on'}
API_KEY=os.getenv('OPENAI_API_KEY','local')
BASE_URL=os.getenv('OPENAI_BASE_URL','https://api.openai.com/v1').rstrip('/')
CHAT_MODEL=os.getenv('CHAT_MODEL','gpt-4o-mini')
IMAGE_MODEL=os.getenv('IMAGE_MODEL','dall-e-3')
HOST=os.getenv('HOST','0.0.0.0')
PORT=int(os.getenv('PORT','7860'))
TEMPERATURE=float(os.getenv('TEMPERATURE','0.4'))
MAX_TOOL_ROUNDS=int(os.getenv('MAX_TOOL_ROUNDS','8'))
MAX_HISTORY_MESSAGES=int(os.getenv('MAX_HISTORY_MESSAGES','30'))
MAX_FILE_CHARS=int(os.getenv('MAX_FILE_CHARS','30000'))
MAX_UPLOAD_MB=int(os.getenv('MAX_UPLOAD_MB','25'))
MEMORY_DB=Path(os.getenv('MEMORY_DB',str(BASE_DIR/'data'/'memory.sqlite3')))
WEB_SEARCH_PROVIDER=os.getenv('WEB_SEARCH_PROVIDER','ddgs').lower()
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY','')
WEB_RESULTS=int(os.getenv('WEB_RESULTS','5'))
WEB_TIMEOUT=int(os.getenv('WEB_TIMEOUT','15'))
SHARE=env_bool('GRADIO_SHARE',False)
WORK_DIR=BASE_DIR/'data'
WORK_DIR.mkdir(parents=True,exist_ok=True)
MEMORY_DB.parent.mkdir(parents=True,exist_ok=True)
