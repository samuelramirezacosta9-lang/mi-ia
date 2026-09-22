import base64,datetime as dt,json,urllib.request
from openai import OpenAI
import config
from tools import TOOLS_SPEC,TOOL_FUNCS
from memory import MEMORY
client=OpenAI(api_key=config.API_KEY,base_url=config.BASE_URL)
SYSTEM_PROMPT="""Eres una inteligencia artificial personal. Responde en el idioma del usuario, con claridad y sin inventar datos. Usa memoria solo cuando sea relevante. Para información actual o cuando el usuario pida Internet, usa search_web y distingue los resultados web del conocimiento general. Puedes analizar archivos y usar herramientas limitadas y seguras."""
def _memory_context(user_text):
    rows=MEMORY.search(user_text,limit=6)
    return "" if not rows else "\n\nMEMORIA RELEVANTE:\n"+"\n".join(f"- {r['text']}" for r in rows)
def chat(messages):
    recent=messages[-config.MAX_HISTORY_MESSAGES:]
    user_text=''
    for m in reversed(recent):
        if m.get('role')=='user': user_text=str(m.get('content','')); break
    convo=[{'role':'system','content':SYSTEM_PROMPT+_memory_context(user_text)}]+recent
    for _ in range(config.MAX_TOOL_ROUNDS):
        resp=client.chat.completions.create(model=config.CHAT_MODEL,messages=convo,tools=TOOLS_SPEC,tool_choice='auto',temperature=config.TEMPERATURE)
        msg=resp.choices[0].message
        if not msg.tool_calls: return msg.content or ''
        convo.append({'role':'assistant','content':msg.content or '','tool_calls':[{'id':tc.id,'type':'function','function':{'name':tc.function.name,'arguments':tc.function.arguments}} for tc in msg.tool_calls]})
        for tc in msg.tool_calls:
            try:
                args=json.loads(tc.function.arguments or '{}'); func=TOOL_FUNCS.get(tc.function.name)
                result=func(**args) if func else f'Herramienta desconocida: {tc.function.name}'
            except Exception as e: result=f'Error ejecutando herramienta: {e}'
            convo.append({'role':'tool','tool_call_id':tc.id,'content':str(result)})
    return 'Se alcanzó el límite de pasos de herramientas.'
def generate_image(prompt):
    resp=client.images.generate(model=config.IMAGE_MODEL,prompt=prompt,n=1,size='1024x1024'); data=resp.data[0]
    path=config.WORK_DIR/f"imagen_{dt.datetime.now():%Y%m%d_%H%M%S}.png"
    if getattr(data,'b64_json',None): path.write_bytes(base64.b64decode(data.b64_json))
    elif getattr(data,'url',None): urllib.request.urlretrieve(data.url,path)
    else: raise RuntimeError('La API no devolvió ninguna imagen.')
    return str(path)
