"""Build a bounded, secret-free context payload for the AI Coach.

The field names here are the agreed application contract, not database schema.
A future Supabase adapter should map real columns into this structure.
"""

import json
from collections.abc import Mapping
from typing import Any


ALLOWED_CONTEXT_FIELDS = (
    "user_profile",
    "fitness_goal",
    "recent_workouts",
    "recent_food_logs",
    "calorie_prediction",
    "recommendation_output",
    "pose_exercise",
    "recent_conversation",
)
SENSITIVE_KEY_NAMES = {
    "api_key",
    "apikey",
    "authorization",
    "access_token",
    "client_secret",
    "cookie",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "service_role_key",
    "token",
}
MAX_CONTEXT_CHARACTERS = 12000
MAX_COLLECTION_ITEMS = 50


def _redact_and_bound(value: Any, depth: int = 0) -> Any:
    """Copy supported JSON data while removing secret-like keys and large values."""
    if depth > 6:
        return "[nested value omitted]"
    if isinstance(value, Mapping):
        return {
            str(key): _redact_and_bound(item, depth + 1)
            for key, item in value.items()
            if str(key).lower() not in SENSITIVE_KEY_NAMES
        }
    if isinstance(value, (list, tuple)):
        return [_redact_and_bound(item, depth + 1) for item in value[:MAX_COLLECTION_ITEMS]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError("context contains a value that cannot be serialized")


def build_context(context: Mapping[str, Any] | None) -> str:
    """Return a safe JSON context string containing only known fields.

    Missing fields are omitted and represented by the prompt as unavailable data.
    Unknown fields are ignored so raw database dumps cannot reach Gemini.
    """
    if context is None:
        return "No user-specific context was supplied."
    if not isinstance(context, Mapping):
        raise ValueError("context must be an object")

    filtered = {
        field: _redact_and_bound(context[field])
        for field in ALLOWED_CONTEXT_FIELDS
        if field in context and context[field] is not None
    }
    serialized = json.dumps(filtered, ensure_ascii=True, separators=(",", ":"))
    if len(serialized) > MAX_CONTEXT_CHARACTERS:
        raise ValueError("context is too large")
    if not filtered:
        return "No user-specific context was supplied."
    return serialized
