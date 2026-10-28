from __future__ import annotations

import queue
import re
import threading
from pathlib import Path
from typing import Any

from core.guardrails import validate_action
from core.mcp_manager import DesktopCommanderManager
from core.paths import APP_ROOT, ensure_writable_dirs
from core.slm_engine import SlmEngine


class TaskRunner:
    """Serial worker. All model inference and MCP I/O occur outside Tkinter's UI thread."""

    def __init__(self) -> None:
        self._tasks: queue.Queue[tuple[str, queue.Queue]] = queue.Queue()
        self._model = SlmEngine()
        self._mcp = DesktopCommanderManager()
        threading.Thread(target=self._run, name="portable-task-runner", daemon=True).start()

    def submit(self, text: str, result_queue: queue.Queue) -> None:
        self._tasks.put((text, result_queue))

    @staticmethod
    def _default_downloads() -> Path:
        home = Path.home()
        candidate = home / "Downloads"
        return candidate if candidate.is_dir() else home

    def _obvious_intent(self, text: str) -> dict[str, Any] | None:
        """Handle the most common read-only commands deterministically before asking the SLM."""
        original = text.strip()
        low = original.casefold()
        if ("herramienta" in low or "tools" in low) and ("mcp" in low or "desktop commander" in low):
            return {"action": "mcp_list_tools", "parameters": {}, "response": ""}

        path_match = re.search(r'([A-Za-z]:\\[^\r\n;]+)', original)
        explicit_path = path_match.group(1).strip().strip("\"'").rstrip(" .") if path_match else None
        if any(token in low for token in ("lista los archivos", "listar archivos", "muestra los archivos", "qué archivos hay", "que archivos hay")):
            if not explicit_path and any(token in low for token in ("descargas", "downloads")):
                explicit_path = str(self._default_downloads())
            return {"action": "list_files", "parameters": {"path": explicit_path} if explicit_path else {}, "response": ""}

        search_match = re.search(r"(?:busca|buscar|encuentra|encontrar)\s+(?:el\s+)?(?:archivo|archivos|carpeta|carpetas)?\s*([^,;]+)", original, re.IGNORECASE)
        if search_match and ("archivo" in low or "carpeta" in low or "busca" in low or "buscar" in low):
            query = search_match.group(1).strip().strip("\"'")
            if query:
                return {"action": "search_files", "parameters": {"path": explicit_path or str(self._default_downloads()), "query": query}, "response": ""}
        return None

    def _execute(self, intent: dict[str, Any]) -> str:
        action = intent["action"]
        params = intent["parameters"]
        check = validate_action(action, params)
        if not check.allowed:
            return f"Acción bloqueada: {check.reason}"

        if action == "chat":
            return intent.get("response") or "¿Puedes concretar un poco más lo que necesitas?"

        if action == "list_files":
            raw_path = params.get("path") or str(self._default_downloads())
            folder = Path(str(raw_path)).expanduser().resolve(strict=False)
            if not folder.is_dir():
                return f"No existe esa carpeta: {folder}"
            # This first release keeps built-in file actions read-only. The folder is chosen
            # by the user/model but no file is changed or deleted.
            try:
                entries = sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold()))[:100]
                if not entries:
                    return f"La carpeta está vacía: {folder}"
                return "Contenido de " + str(folder) + ":\n" + "\n".join(
                    ("[DIR] " if item.is_dir() else "[FILE] ") + item.name for item in entries
                )
            except OSError as exc:
                return f"No he podido leer la carpeta: {exc}"

        if action == "search_files":
            raw_path = params.get("path") or str(self._default_downloads())
            query = str(params.get("query") or "").strip().casefold()
            if not query:
                return "Falta el nombre o texto que quieres buscar."
            folder = Path(str(raw_path)).expanduser().resolve(strict=False)
            if not folder.is_dir():
                return f"No existe esa carpeta: {folder}"
            found = []
            try:
                for path in folder.rglob("*"):
                    if query in path.name.casefold():
                        found.append(str(path))
                        if len(found) >= 100:
                            break
            except (OSError, PermissionError) as exc:
                return f"La búsqueda se ha detenido por permisos: {exc}"
            return "Coincidencias:\n" + "\n".join(found) if found else "No se encontraron coincidencias."

        if action == "mcp_list_tools":
            tools = self._mcp.list_tools()
            return "Herramientas disponibles en Desktop Commander (solo listado; no se ejecutó ninguna):\n" + "\n".join(
                f"• {tool['name']}: {tool['description']}" for tool in tools
            )

        if action == "organize_files":
            return "La organización de archivos está bloqueada en esta versión inicial. Primero añadiremos vista previa y confirmación explícita."

        return "No existe un ejecutor para esa acción. No se ha ejecutado nada."

    def _run(self) -> None:
        ensure_writable_dirs()
        while True:
            task, result_queue = self._tasks.get()
            try:
                intent = self._obvious_intent(task)
                if intent is None:
                    result_queue.put(("progress", "Interpretando la orden con el modelo local…"))
                    intent = self._model.interpret(task)
                else:
                    result_queue.put(("progress", "Orden de consulta reconocida por las reglas locales…"))
                result = self._execute(intent)
                result_queue.put(("done", result))
            except Exception as exc:
                result_queue.put(("done", f"Error: {type(exc).__name__}: {exc}"))
            finally:
                self._tasks.task_done()
