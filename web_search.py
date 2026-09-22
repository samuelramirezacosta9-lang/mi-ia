import requests,config
def search_web(query,max_results=None):
 query=(query or '').strip()
 if not query:return 'Consulta web vacía.'
 max_results=max(1,min(10,int(max_results or config.WEB_RESULTS)))
 if config.WEB_SEARCH_PROVIDER=='tavily':
  if not config.TAVILY_API_KEY:return 'Tavily seleccionado pero no hay clave.'
  try:r=requests.post('https://api.tavily.com/search',json={'api_key':config.TAVILY_API_KEY,'query':query,'max_results':max_results},timeout=config.WEB_TIMEOUT);r.raise_for_status();results=r.json().get('results',[])
  except Exception as e:return f'Error en búsqueda web: {e}'
 else:
  try:
   from ddgs import DDGS; results=list(DDGS().text(query,max_results=max_results))
  except Exception as e:return f'Error en búsqueda web DDGS: {e}'
 if not results:return 'No se encontraron resultados.'
 return '\n\n'.join(f"{i}. {x.get('title','Sin título')}\nURL: {x.get('href') or x.get('url','')}\nResumen: {x.get('body') or x.get('content','')}" for i,x in enumerate(results,1))
