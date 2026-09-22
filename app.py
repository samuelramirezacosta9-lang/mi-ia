"""Interfaz web local de la IA."""
import uuid
import gradio as gr
import config
from assistant import chat, generate_image
from file_handler import analyze_file
from memory import MEMORY

def responder(mensaje, historial, archivos, session_id):
    historial = historial or []
    content_parts = []
    text = mensaje or ""
    if archivos:
        for ruta in archivos:
            try:
                tipo, contenido = analyze_file(ruta)
                if tipo == "image":
                    content_parts.append({"type":"image_url","image_url":{"url":contenido}})
                else:
                    text += "\n\n" + contenido
            except Exception as e:
                text += f"\n\n[Error con archivo: {e}]"
    content_parts.insert(0, {"type":"text","text":text or "(sin texto)"})
    api_messages = []
    for m in historial:
        if m.get("role") in {"user","assistant"}:
            api_messages.append({"role":m["role"],"content":m["content"]})
    api_messages.append({"role":"user","content":content_parts})
    MEMORY.add_message(session_id, "user", text)
    try:
        answer = chat(api_messages)
    except Exception as e:
        answer = f"Error al contactar el modelo: {e}"
    MEMORY.add_message(session_id, "assistant", answer)
    return answer

def turno(mensaje, historial, files, session_id):
    historial = historial or []
    user_display = mensaje or "(archivo adjunto)"
    if files:
        user_display += "\n\n[Archivo(s) adjunto(s)]"
    historial.append({"role":"user","content":user_display})
    answer = responder(mensaje, historial[:-1], files, session_id)
    historial.append({"role":"assistant","content":answer})
    return historial, "", None

def new_session():
    return [], "", None, str(uuid.uuid4())

def crear_imagen(prompt):
    if not prompt.strip():
        return None, "Escribe una descripción."
    try:
        path = generate_image(prompt)
        return path, "Imagen generada."
    except Exception as e:
        return None, f"Error: {e}"

def memory_view():
    rows = MEMORY.list_memories()
    if not rows: return "No hay memorias guardadas."
    return "\n".join(f"ID {r['id']} | {r['kind']} | {r['importance']}/5 | {r['text']}" for r in rows)

with gr.Blocks(title="Mi IA Local") as demo:
    gr.Markdown("# Mi IA Local\nChat, memoria persistente, archivos, herramientas y búsqueda web.")
    session = gr.State(str(uuid.uuid4()))
    with gr.Tab("Chat"):
        chatbot = gr.Chatbot(type="messages", height=520)
        archivos = gr.File(label="Adjuntar archivos", file_count="multiple", type="filepath",
                           file_types=[".pdf",".docx",".csv",".xlsx",".xls",".txt",".md",".json",".py",".js",".html",".css",".png",".jpg",".jpeg",".webp"])
        with gr.Row():
            entrada = gr.Textbox(placeholder="Escribe un mensaje...", scale=8, show_label=False)
            enviar = gr.Button("Enviar", variant="primary")
        limpiar = gr.Button("Nueva conversación")
        enviar.click(turno,[entrada,chatbot,archivos,session],[chatbot,entrada,archivos])
        entrada.submit(turno,[entrada,chatbot,archivos,session],[chatbot,entrada,archivos])
        limpiar.click(new_session,outputs=[chatbot,entrada,archivos,session])

    with gr.Tab("Memoria"):
        gr.Markdown("La memoria se almacena localmente en SQLite.")
        ver = gr.Button("Actualizar")
        memorias = gr.Textbox(lines=15, interactive=False)
        ver.click(memory_view, outputs=memorias)

    with gr.Tab("Generar imagen"):
        prompt = gr.Textbox(label="Descripción", lines=3)
        btn = gr.Button("Generar", variant="primary")
        img = gr.Image(type="filepath")
        estado = gr.Textbox(interactive=False)
        btn.click(crear_imagen,prompt,[img,estado])

    with gr.Tab("Ayuda"):
        gr.Markdown("""### Funciones
- Memoria persistente local y recuperable.
- Búsqueda web mediante DDGS o Tavily.
- PDF, DOCX, CSV, Excel, texto e imágenes.
- Herramientas: cálculo seguro, fecha/hora, archivos y memoria.
- Generación de imágenes si el proveedor configurado la soporta.

### Seguridad
La interfaz escucha en 127.0.0.1 por defecto. No uses `GRADIO_SHARE=true`
si no quieres exponerla. Los archivos tienen límite de tamaño y extensiones.
""")

if __name__ == "__main__":
    demo.launch(server_name=config.HOST, server_port=config.PORT, share=config.SHARE)
