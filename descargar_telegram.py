"""Módulo opcional de Telegram. No se inicia ni conecta por defecto.

Para habilitarlo habrá que añadir credenciales propias de Telegram al archivo
local de datos. No se incluyen credenciales ni claves en el ejecutable.
"""

from __future__ import annotations


def verify_telethon_available() -> tuple[bool, str]:
    try:
        import telethon  # noqa: F401
        return True, "Telethon está incluido en el ejecutable."
    except Exception as exc:
        return False, f"Telethon no está disponible en esta compilación: {exc}"


if __name__ == "__main__":
    print(verify_telethon_available()[1])
