"""HTTP transport helpers for external concept extraction providers."""

from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

HTTP_REQUEST_TIMEOUT_SECONDS = 60


def post_json(
    *,
    provider_name: str,
    url: str,
    headers: dict[str, str],
    body: dict[str, Any],
) -> dict[str, Any]:
    """POST a JSON body and return the decoded JSON response."""
    encoded_body = json.dumps(body).encode("utf-8")
    request = urllib_request.Request(
        url=url,
        data=encoded_body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib_request.urlopen(
            request,
            timeout=HTTP_REQUEST_TIMEOUT_SECONDS,
        ) as response:
            raw_response = response.read().decode("utf-8")
    except urllib_error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"{provider_name} API request failed with status {exc.code}: {error_body}"
        ) from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(f"{provider_name} API request failed: {exc.reason}") from exc

    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{provider_name} API returned invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{provider_name} API returned a non-object JSON payload.")
    return payload
