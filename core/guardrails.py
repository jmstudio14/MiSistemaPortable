from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationResult:
    allowed: bool
    reason: str


READ_ONLY_ACTIONS = {"chat", "list_files", "search_files", "mcp_list_tools"}
SENSITIVE_ACTIONS = {"organize_files", "delete_files", "run_command", "mcp_call_tool"}


def validate_action(action_name: str, parameters: dict) -> ValidationResult:
    """Fail closed: unknown actions are denied, and execution is never inferred from text alone."""
    if not isinstance(parameters, dict):
        return ValidationResult(False, "Los parámetros deben ser un objeto JSON.")
    if action_name in READ_ONLY_ACTIONS:
        return ValidationResult(True, "Acción de consulta permitida.")
    if action_name in SENSITIVE_ACTIONS:
        return ValidationResult(False, "La acción necesita una confirmación explícita y una política específica.")
    return ValidationResult(False, f"Acción no autorizada: {action_name}")


def is_within(path: Path, roots: list[Path]) -> bool:
    """Return True only when a resolved path is under one of the allowed roots."""
    try:
        resolved = path.expanduser().resolve(strict=False)
    except (OSError, RuntimeError):
        return False
    for root in roots:
        try:
            resolved.relative_to(root.expanduser().resolve(strict=False))
            return True
        except (ValueError, OSError, RuntimeError):
            continue
    return False
