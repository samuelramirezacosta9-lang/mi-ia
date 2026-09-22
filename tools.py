import ast,datetime as dt,math,os
from config import WORK_DIR
from memory import MEMORY
from web_search import search_web
_ALLOWED_FUNCS={k:getattr(math,k) for k in dir(math) if not k.startswith('_')}
_ALLOWED_FUNCS.update({'abs':abs,'round':round,'min':min,'max':max,'sum':sum})
def get_current_time(): return dt.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z (%A)')
def calculate(expression):
 try:
  tree=ast.parse(expression,mode='eval'); allowed=(ast.Expression,ast.BinOp,ast.UnaryOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.Mod,ast.FloorDiv,ast.USub,ast.UAdd,ast.Constant,ast.Call,ast.Name,ast.Load,ast.Tuple)
  for n in ast.walk(tree):
   if not isinstance(n,allowed): raise ValueError('Operación no permitida')
   if isinstance(n,ast.Name) and n.id not in _ALLOWED_FUNCS: raise ValueError('Nombre no permitido')
   if isinstance(n,ast.Call) and (not isinstance(n.func,ast.Name) or n.func.id not in _ALLOWED_FUNCS): raise ValueError('Función no permitida')
  return f"{expression} = {eval(compile(tree,'<calculator>','eval'),{'__builtins__':{}},_ALLOWED_FUNCS)}"
 except Exception as e:return f"Error al calcular '{expression}': {e}"
def save_text_file(filename,content):
 path=WORK_DIR/os.path.basename(filename); path.write_text(content,encoding='utf-8'); return f'Archivo guardado en: {path}'
def list_saved_files():
 fs=sorted(p.name for p in WORK_DIR.iterdir() if p.is_file()); return 'No hay archivos guardados todavía.' if not fs else 'Archivos guardados:\n'+'\n'.join('- '+f for f in fs)
def remember(text,kind='fact',importance=3): MEMORY.add_memory(text,kind,importance); return f'Memoria guardada: {text}'
def recall(query):
 rows=MEMORY.search(query); return 'No encontré recuerdos relevantes.' if not rows else 'Recuerdos relevantes:\n'+'\n'.join(f"- {r['text']} (importancia {r['importance']}/5)" for r in rows)
def forget(memory_id): return 'Memoria eliminada.' if MEMORY.delete_memory(memory_id) else 'No existe una memoria con ese ID.'
TOOLS_SPEC=[
{'type':'function','function':{'name':'get_current_time','description':'Obtiene fecha y hora local.','parameters':{'type':'object','properties':{}}}},
{'type':'function','function':{'name':'calculate','description':'Calcula expresiones matemáticas seguras.','parameters':{'type':'object','properties':{'expression':{'type':'string'}},'required':['expression']}}},
{'type':'function','function':{'name':'search_web','description':'Busca información actual en Internet.','parameters':{'type':'object','properties':{'query':{'type':'string'},'max_results':{'type':'integer','minimum':1,'maximum':10}},'required':['query']}}},
{'type':'function','function':{'name':'remember','description':'Guarda un recuerdo.','parameters':{'type':'object','properties':{'text':{'type':'string'},'kind':{'type':'string'},'importance':{'type':'integer'}},'required':['text']}}},
{'type':'function','function':{'name':'recall','description':'Busca recuerdos.','parameters':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}}},
{'type':'function','function':{'name':'forget','description':'Elimina un recuerdo por ID.','parameters':{'type':'object','properties':{'memory_id':{'type':'integer'}},'required':['memory_id']}}},
{'type':'function','function':{'name':'save_text_file','description':'Guarda texto.','parameters':{'type':'object','properties':{'filename':{'type':'string'},'content':{'type':'string'}},'required':['filename','content']}}},
{'type':'function','function':{'name':'list_saved_files','description':'Lista archivos guardados.','parameters':{'type':'object','properties':{}}}}]
TOOL_FUNCS={x['function']['name']:globals()[x['function']['name']] for x in TOOLS_SPEC}
