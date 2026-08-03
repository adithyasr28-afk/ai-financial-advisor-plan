import json
import httpx


def get_bytes(url: str, headers: dict[str, str] | None = None) -> bytes:
    response = httpx.get(url, headers=headers or {"User-Agent": "AI-Financial-Advisor/0.1"}, timeout=30)
    response.raise_for_status()
    return response.content


def get_json(url: str, headers: dict[str, str] | None = None) -> dict:
    return json.loads(get_bytes(url, headers).decode("utf-8"))
