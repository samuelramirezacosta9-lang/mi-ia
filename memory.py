import datetime as dt,sqlite3
class MemoryStore:
 def __init__(self,db_path):
  self.db_path=str(db_path); self._init_db()
 def _connect(self):
  c=sqlite3.connect(self.db_path); c.row_factory=sqlite3.Row; return c
 def _init_db(self):
  with self._connect() as c:
   c.execute("CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY AUTOINCREMENT,session_id TEXT,role TEXT,content TEXT,created_at TEXT)")
   c.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY AUTOINCREMENT,text TEXT UNIQUE,kind TEXT DEFAULT 'fact',importance INTEGER DEFAULT 3,created_at TEXT,updated_at TEXT)")
 def add_message(self,s,r,content):
  if content:
   with self._connect() as c:c.execute("INSERT INTO conversations(session_id,role,content,created_at) VALUES(?,?,?,?)",(s,r,content,dt.datetime.now().isoformat(timespec='seconds')))
 def add_memory(self,text,kind='fact',importance=3):
  text=text.strip()
  if not text:return False
  now=dt.datetime.now().isoformat(timespec='seconds')
  with self._connect() as c:c.execute("INSERT INTO memories(text,kind,importance,created_at,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(text) DO UPDATE SET kind=excluded.kind,importance=excluded.importance,updated_at=excluded.updated_at",(text,kind,max(1,min(5,int(importance))),now,now))
  return True
 def delete_memory(self,i):
  with self._connect() as c:return c.execute("DELETE FROM memories WHERE id=?",(i,)).rowcount>0
 def list_memories(self,limit=100):
  with self._connect() as c:return c.execute("SELECT * FROM memories ORDER BY importance DESC,updated_at DESC LIMIT ?",(limit,)).fetchall()
 def search(self,q,limit=8):
  terms=[t for t in q.replace('"',' ').split() if len(t)>2][:8]
  if not terms:return []
  like='%'+terms[0]+'%'
  with self._connect() as c:return c.execute("SELECT * FROM memories WHERE text LIKE ? ORDER BY importance DESC LIMIT ?",(like,limit)).fetchall()
MEMORY=MemoryStore(__import__('config').MEMORY_DB)
