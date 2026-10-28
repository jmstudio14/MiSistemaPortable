from __future__ import annotations

import json
import os
from typing import Any

from core.json_parser import extract_json_object
from core.paths import MODEL_PATH


class SlmEngine:
    """Lazy, in-process llama.cpp model. No local server or Ollama is used."""

    ACTIONS = {"chat", "list_files", "search_files", "organize_files", "mcp_list_tools"}

    def __init__(self) -> None:
        self._model = None

    def load(self) -> None:
        if self._model is not None:
            return
        if not MODEL_PATH.is_file():
            raise FileNotFoundError(
                "No se encontró el modelo GGUF incluido. Vuelve a generar el ejecutable con build_portable.bat."
            )
        from llama_cpp import Llama

        cpu_count = os.cpu_count() or 4
        self._model = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=2048,
            n_threads=max(2, min(cpu_count, 8)),
            verbose=False,
        )

    def interpret(self, user_text: str) -> dict[str, Any]:
        self.load()
        system_prompt = (
            "Eres el intérprete de órdenes de un automatizador LOCAL de Windows. "
            "Devuelve solamente un objeto JSON con claves action, parameters y response. "
            "Acciones permitidas: chat, list_files, search_files, organize_files, mcp_list_tools. "
            "No inventes ejecución, no generes comandos de PowerShell/CMD, no solicites claves. "
            "Para chat: response contiene una respuesta breve en español. "
            "Para list_files: parameters puede incluir path. Para search_files: parameters incluye path y query. "
            "organize_files es una acción sensible y no se ejecutará sin confirmación. "
            "Si no comprendes con claridad, usa chat y explica la duda."
        )
        result = self._model.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=0.0,
            max_tokens=256,
            response_format={"type": "json_object"},
        )
        content = result["choices"][0]["message"].get("content", "")
        parsed = extract_json_object(content)
        if not parsed:
            return {"action": "chat", "parameters": {}, "response": "No he podido interpretar esa orden con seguridad. Reformúlala de forma más concreta."}

        action = parsed.get("action")
        parameters = parsed.get("parameters", {})
        response = parsed.get("response", "")
        if action not in self.ACTIONS or not isinstance(parameters, dict):
            return {"action": "chat", "parameters": {}, "response": "La respuesta del modelo no superó la validación. No se ejecutó ninguna acción."}
        return {"action": action, "parameters": parameters, "response": str(response)[:2000]}
