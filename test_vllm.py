import argparse
import json

import gradio as gr
import requests

def get_default_model():
    """Obtener el ID del modelo predeterminado desde el servidor."""
    response_model = requests.get("http://localhost:8000/v1/models")
    if response_model.status_code == 200:
        return response_model.json()["data"][0]["id"]
    else:
        raise Exception("Failed to fetch model information")

def build_messages(history, max_tokens=1024):
    """Construye y trunca el historial de mensajes para mantenerse dentro del límite de tokens."""
    messages = []
    total_length = 0

    # Recorrer el historial desde el más reciente hasta el más antiguo
    for msg, reply in reversed(history):
        msg_length = len(msg) + len(reply) + 2  # +2 for role labels
        if total_length + msg_length > max_tokens:
            break
        # Prepend to keep the order after reversing
        messages.insert(0, {"role": "user", "content": msg})
        messages.insert(1, {"role": "assistant", "content": reply})
        total_length += msg_length

    return messages

def chatbot_function(history):
    """Función que interactúa con el modelo de lenguaje para obtener respuestas."""
    headers = {"User-Agent": "vLLM Client"}
    pload = {
        "model": MODEL,
        "messages": build_messages(history),
        "stream": True,
        "max_tokens": 128,
        "temperature": 0.0,
    }
    response = requests.post(args.model_url, headers=headers, json=pload, stream=True)

    for chunk in response.iter_lines(chunk_size=8192, decode_unicode=True):
        if chunk:
            text = chunk.lstrip('data: ')
            if text == '[DONE]':
                break
            data = json.loads(text)
            delta = data["choices"][0]["delta"]
            if "content" in delta:
                history[-1][1] += delta["content"]
                yield history


def build_chatbot_demo():
    """Construye la interfaz de Gradio utilizando el componente Chatbot."""
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

        def user(user_message, history):
            return "", history + [[user_message, ""]]

        msg.submit(user, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False).then(
            chatbot_function, inputs=chatbot, outputs=chatbot
        )
        clear.click(lambda: ("", []), inputs=None, outputs=[msg, chatbot], queue=False)
    
    return demo.queue()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default=None)
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument(
        "--model-url", type=str, default="http://localhost:8000/v1/chat/completions"
    )
    args = parser.parse_args()

    MODEL = get_default_model()
    demo = build_chatbot_demo()
    demo.launch(
        server_name=args.host, server_port=args.port, share=False
    )
