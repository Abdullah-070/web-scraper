"""
Shared input validation helpers 
"""

from __future__ import annotations

from typing import Any

from shared.exceptions import InvalidInputError


def require_str(params: dict[str, Any], field_name: str, strip: bool = True) -> str:
    """Return params[field_name] as a string, raising InvalidInputError
    
    """
    value = params.get(field_name)

    if value is None or value == "":
        raise InvalidInputError(
            f"Missing required field: {field_name}",
            details={"missing_fields": [field_name]},
        )

    if not isinstance(value, str):
        raise InvalidInputError(
            f"Field '{field_name}' must be a string, got {type(value).__name__}.",
            details={"field": field_name, "received_type": type(value).__name__},
        )

    return value.strip() if strip else value


def optional_str(params: dict[str, Any], field_name: str) -> str | None:
    """for optional fields that still need to reject a wrong
    type when present 
    """
    value = params.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise InvalidInputError(
            f"Field '{field_name}' must be a string if provided, got {type(value).__name__}.",
            details={"field": field_name, "received_type": type(value).__name__},
        )
    return value
