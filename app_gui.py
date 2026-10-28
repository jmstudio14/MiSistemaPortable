from __future__ import annotations

import queue
import tkinter as tk
from tkinter import ttk, messagebox

from core.paths import APP_ROOT
from core.task_runner import TaskRunner


class PortableApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MiSistemaPortable")
        self.geometry("900x640")
        self.minsize(720, 480)
        self.runner = TaskRunner()
        self.messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self._build_ui()
        self.after(100, self._poll_messages)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="MiSistemaPortable", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Modelo local · MCP local · Sin llamadas a APIs de IA en la nube",
            wraplength=850,
        ).pack(anchor="w", pady=(2, 2))
        ttk.Label(outer, text=f"Ejecutable/carpeta portable: {APP_ROOT}", wraplength=850).pack(anchor="w", pady=(0, 10))

        self.output = tk.Text(outer, wrap="word", state="disabled", font=("Consolas", 10), height=20)
        self.output.pack(fill="both", expand=True)
        bottom = ttk.Frame(outer)
        bottom.pack(fill="x", pady=(10, 0))
        self.entry = ttk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._submit)
        self.send_button = ttk.Button(bottom, text="Enviar", command=self._submit)
        self.send_button.pack(side="left", padx=(8, 0))
        self._append("Iniciado. El modelo se carga la primera vez que envías una orden.")
        self._append("Pruebas sugeridas: «lista los archivos de Descargas» o «lista las herramientas MCP».")
        self._append("Las operaciones de escritura, borrado y comandos arbitrarios están bloqueadas por defecto.")

    def _submit(self, _event=None) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._append(f"Tú: {text}")
        self.send_button.configure(state="disabled")
        self.runner.submit(text, self.messages)

    def _poll_messages(self) -> None:
        try:
            while True:
                kind, message = self.messages.get_nowait()
                if kind == "progress":
                    self._append(f"Sistema: {message}")
                else:
                    self._append(f"Asistente: {message}")
                    self.send_button.configure(state="normal")
        except queue.Empty:
            pass
        self.after(100, self._poll_messages)

    def _append(self, message: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", message + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def _on_close(self) -> None:
        if messagebox.askokcancel("Cerrar", "¿Quieres cerrar MiSistemaPortable?"):
            self.destroy()


if __name__ == "__main__":
    PortableApp().mainloop()
