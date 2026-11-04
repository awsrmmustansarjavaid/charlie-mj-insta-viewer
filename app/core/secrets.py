"""Credential storage in Windows Credential Manager (via ``keyring``).

Tokens are never written to the database, settings, logs or exports. If no
keyring backend is available the token is kept in memory for the session only.
"""

from __future__ import annotations

_SERVICE = "InstagramResearchSuite"
_memory: dict[str, str] = {}


def _kr():
    try:
        import keyring

        return keyring
    except Exception:  # noqa: BLE001
        return None


def set_secret(key: str, value: str) -> bool:
    """Store a secret. Returns True when persisted in the OS keyring."""
    _memory[key] = value
    kr = _kr()
    if kr:
        try:
            kr.set_password(_SERVICE, key, value)
            return True
        except Exception:  # noqa: BLE001
            return False
    return False


def get_secret(key: str) -> str:
    """Fetch a secret from memory or the OS keyring."""
    if key in _memory:
        return _memory[key]
    kr = _kr()
    if kr:
        try:
            return kr.get_password(_SERVICE, key) or ""
        except Exception:  # noqa: BLE001
            return ""
    return ""


def delete_secret(key: str) -> None:
    """Remove a secret everywhere."""
    _memory.pop(key, None)
    kr = _kr()
    if kr:
        try:
            kr.delete_password(_SERVICE, key)
        except Exception:  # noqa: BLE001
            pass
