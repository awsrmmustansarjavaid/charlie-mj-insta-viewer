# Providers

## Capability matrix
| Feature | Demo | Graph API | Data export |
|---|---|---|---|
| Profile | ✅ | ✅ own + other Business/Creator (business_discovery) | – |
| Followers / Following lists | ✅ | ⛔ counts only | ✅ complete, own account |
| Posts / reels | ✅ | ✅ | – |
| Comments + replies (+ reply) | ✅ | ✅ own media | – |
| Stories | ✅ | ✅ own, active | – |
| Highlights | ✅ | ⛔ | – |
| Mentions / tags | ✅ | 🟡 tagged media + captions | – |
| Audience gender / age / country | ✅ simulated | 🟡 aggregate, ≥100 followers | – |

## Graph API setup
1. Instagram Business/Creator account linked to a Facebook Page; create a Meta app.
2. Generate a token with `instagram_basic`, `instagram_manage_comments`, `instagram_manage_insights` (some need Meta app review for use beyond your own accounts).
3. Provider manager → enter token, Instagram user ID, username → *Save & test*.
Token storage: Windows Credential Manager via `keyring` (memory-only if unavailable). Only HTTPS is used. Endpoint names/versions change; adjust `api_version` in the form.

## Writing a provider
```python
from app.providers.base import Provider, ProviderError, Capability, AVAILABLE, NOT_PUBLIC

class MySource(Provider):
    name, label = "mine", "My authorised source"
    def capabilities(self): return [Capability("profile", "Profile", AVAILABLE)]
    def get_profile(self, username): ...           # return ProfileInfo
    # anything unsupported falls through to Provider's ProviderError(NOT_PUBLIC)
```
Register it in `ProviderRegistry.reload()`. Return `RetrievalStatus(complete=False, …)` for partial lists; the UI will show "Partial" instead of claiming completeness. Only integrate sources you are permitted to use.
