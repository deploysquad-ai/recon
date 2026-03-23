"""JSON Schema export from Pydantic models."""
from __future__ import annotations

from .models import NODE_TYPE_MAP


def export_schema(node_type: str) -> dict:
    """Export JSON Schema dict for a single node type.

    Raises KeyError if the type is not registered.
    """
    model = NODE_TYPE_MAP[node_type]
    return model.model_json_schema()


def export_schemas() -> dict[str, dict]:
    """Export JSON Schema dicts for all registered node types."""
    return {name: model.model_json_schema() for name, model in NODE_TYPE_MAP.items()}
