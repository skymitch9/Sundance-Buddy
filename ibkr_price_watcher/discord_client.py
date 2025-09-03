from __future__ import annotations

from typing import Optional
import requests

def post_discord(webhook_url: str, content: str, username: Optional[str] = None) -> None:
    """
    Post a simple text message to a Discord webhook.
    """
    if not webhook_url:
        return
    payload = {"content": content}
    if username:
        payload["username"] = username
    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[WARN] Discord webhook failed: {e}")
