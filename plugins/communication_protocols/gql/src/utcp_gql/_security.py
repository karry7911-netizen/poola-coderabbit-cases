
from __future__ import annotations

from contextlib import asynccontextmanager
from ipaddress import ip_address
from typing import Any, AsyncIterator, Optional
from urllib.parse import urljoin, urlparse

# Hostnames considered safe to talk to over plain HTTP.
_LOOPBACK_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "::1", "[::1]"})


def is_secure_url(url: str) -> bool:
    if not isinstance(url, str) or not url:
        return False

    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    scheme = (parsed.scheme or "").lower()
    if scheme not in {"http", "https"}:
        return False

    host = (parsed.hostname or "").lower()
    if not host:
        return False

    if scheme == "https":
        return True

    # http:// is only allowed for loopback.
    if host in _LOOPBACK_HOSTNAMES:
        return True

    # Catch any other literal loopback IP that urlparse normalised
    # (e.g. ``http://127.000.000.001``).
    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


def is_loopback_url(url: str) -> bool:
    """Return True if ``url``'s host is a literal loopback address.

    Used by the OpenAPI converter to detect the SSRF case where a remote spec
    declares ``servers: [{ url: "http://127.0.0.1:..." }]`` to redirect tool
    invocation at the host running the agent. Hostname-based — not a string
    prefix — so ``http://localhost.evil.com`` returns False.
    """
    if not isinstance(url, str) or not url:
        return False

    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    host = (parsed.hostname or "").lower()
    if not host:
        return False

    if host in _LOOPBACK_HOSTNAMES:
        return True

    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


def ensure_secure_url(url: str, *, context: Optional[str] = None) -> None:
    """Raise ``ValueError`` if ``url`` is not safe to fetch.

    ``context`` is a short label (``"manual discovery"``, ``"tool invocation"``,
    etc.) included in the error so log readers can tell which trust boundary
    was breached.
    """
    if is_secure_url(url):
        return

    where = f" during {context}" if context else ""
    raise ValueError(
        f"Security error{where}: URL must use HTTPS or be a literal loopback "
        f"address (localhost / 127.0.0.1 / ::1). Got: {url!r}. "
        "Plain HTTP to any other host is rejected to prevent MITM attacks "
        "and SSRF into internal services."
    )


# HTTP statuses where the server expects the client to re-issue the request
# against the URL given in the ``Location`` header. 303 forces a GET; the
# rest preserve the original method.
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})


@asynccontextmanager
async def safe_request_with_redirects(
    session: Any,
    method: str,
    url: str,
    *,
    context: str,
    max_redirects: int = 5,
    **kwargs: Any,
) -> AsyncIterator[Any]:
    ensure_secure_url(url, context=context)
    # We control redirect behavior ourselves; refuse to let callers override.
    kwargs.pop("allow_redirects", None)

    current_url = url
    current_method = method
    hops = 0
    final_response = None

    try:
        while True:
            response = await session.request(
                current_method,
                current_url,
                allow_redirects=False,
                **kwargs,
            )
            if response.status not in _REDIRECT_STATUSES:
                final_response = response
                break

            location = response.headers.get("Location")
            if not location:
                # 3xx with no Location header — nothing to follow. Let
                # the caller handle the unusual response.
                final_response = response
                break

            if hops >= max_redirects:
                response.release()
                raise RuntimeError(
                    f"Too many redirects (>{max_redirects}) during {context} "
                    f"starting from {url!r}."
                )

            next_url = urljoin(current_url, location)
            try:
                ensure_secure_url(
                    next_url, context=f"{context} (redirect target)"
                )
            except Exception:
                response.release()
                raise

            response.release()
            if response.status == 303:
                current_method = "GET"
                kwargs.pop("json", None)
                kwargs.pop("data", None)
            current_url = next_url
            hops += 1

        yield final_response
    finally:
        if final_response is not None:
            final_response.release()
