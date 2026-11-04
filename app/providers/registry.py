"""Provider registry: selection, health checks and automatic fallback."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.core.secrets import get_secret
from app.providers.base import Provider, ProviderError
from app.providers.demo import DemoProvider
from app.providers.graph_api import GraphApiProvider

log = logging.getLogger(__name__)


@dataclass
class ProviderHealth:
    ok: bool
    ms: int
    message: str
    checked_at: float


class ProviderRegistry:
    """Holds providers; the active one serves requests, others are fallbacks."""

    def __init__(self, db):
        self.db = db
        self.health: dict[str, ProviderHealth] = {}
        self.providers: dict[str, Provider] = {}
        self.reload()

    def reload(self) -> None:
        """Rebuild providers from saved settings (tokens come from the keyring)."""
        epoch = int(self.db.get_setting("demo_epoch", 0))
        self.providers = {
            "demo": DemoProvider(epoch),
            "graph": GraphApiProvider(
                access_token=get_secret("graph_token"),
                ig_user_id=str(self.db.get_setting("graph_user_id", "")),
                username=str(self.db.get_setting("graph_username", "")),
                api_version=str(self.db.get_setting("graph_version", "v23.0")),
            ),
        }

    @property
    def active_name(self) -> str:
        return str(self.db.get_setting("active_provider", "demo"))

    def enabled(self, name: str) -> bool:
        return bool(self.db.get_setting(f"provider_enabled_{name}", True))

    @property
    def active(self) -> Provider:
        return self.providers.get(self.active_name) or self.providers["demo"]

    def order(self) -> list[Provider]:
        """Active first, then other enabled *real* providers (fallback order).

        The demo provider is never used as a silent fallback, so fictional data
        can never appear to be the result of a real lookup.
        """
        names = [self.active_name] + [n for n in self.providers
                                      if n != self.active_name and n != "demo"]
        return [self.providers[n] for n in names if n in self.providers and self.enabled(n)]

    def check(self, name: str) -> ProviderHealth:
        start = time.perf_counter()
        ok, ms, msg = self.providers[name].health()
        h = ProviderHealth(ok, ms or int((time.perf_counter() - start) * 1000), msg, time.time())
        self.health[name] = h
        return h

    def call(self, method: str, *args, fallback: bool = True, **kwargs):
        """Call ``method`` on the active provider; on failure try the next.

        Raises the first :class:`ProviderError` if every provider fails.
        """
        first: ProviderError | None = None
        for prov in self.order() if fallback else [self.active]:
            try:
                return getattr(prov, method)(*args, **kwargs)
            except ProviderError as exc:
                log.warning("%s.%s failed: %s", prov.name, method, exc)
                first = first or exc
        raise first or ProviderError("No provider is enabled.")
