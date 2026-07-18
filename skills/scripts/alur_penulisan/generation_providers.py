"""Provider adapters for guarded TA content generation.

Two deliberately small integrations are included:

* :class:`ResponseFileProvider` reads a structured JSON candidate produced by
  any AI agent.  It is deterministic and suitable for review/testing.
* :class:`HttpJsonProvider` posts the provider-neutral request JSON to an HTTP
  adapter and expects either the candidate object directly or under a
  ``candidate`` field.  No vendor SDK, endpoint, model, or secret is hard-coded.

Remote calls receive only the request assembled by ``agentic_generation``.
Facts are data-minimised there: only keys explicitly selected by the caller are
sent.  Tokens stay in environment variables/CLI memory and are never persisted
by this module.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from .agentic_generation import GenerationCandidate, GenerationRequest

__all__ = ["HttpJsonProvider", "ResponseFileProvider"]


def _candidate_mapping(payload: Any) -> Mapping[str, Any]:
    """Extract a candidate mapping from the supported adapter envelopes."""

    if not isinstance(payload, Mapping):
        raise ValueError("provider response must be a JSON object")

    if isinstance(payload.get("candidate"), Mapping):
        return payload["candidate"]

    if "section_id" in payload and "markdown" in payload:
        return payload

    # Lightweight adapters may wrap JSON text in a ``content`` field.
    content = payload.get("content")
    if isinstance(content, str):
        try:
            decoded = json.loads(content)
        except ValueError as exc:
            raise ValueError("provider 'content' field is not valid JSON") from exc
        return _candidate_mapping(decoded)

    raise ValueError(
        "provider response must contain a candidate object or direct section_id/markdown fields"
    )


@dataclass(frozen=True)
class ResponseFileProvider:
    """Load a structured candidate from a local JSON file."""

    path: str

    def generate(self, request: GenerationRequest) -> GenerationCandidate:
        del request  # the response is already materialised by another agent
        with open(self.path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return GenerationCandidate.from_mapping(_candidate_mapping(payload))


@dataclass(frozen=True)
class HttpJsonProvider:
    """POST the provider-neutral generation request to an HTTP adapter.

    Adapter contract:

    * request: ``GenerationRequest.to_mapping()`` as UTF-8 JSON;
    * response: a direct candidate object, ``{"candidate": {...}}``, or
      ``{"content": "{...json...}"}``;
    * optional bearer token: supplied by the caller, never read from a file.
    """

    endpoint: str
    bearer_token: str | None = None
    timeout_seconds: float = 120.0
    model: str | None = None

    def generate(self, request: GenerationRequest) -> GenerationCandidate:
        payload = request.to_mapping()
        if self.model:
            payload["provider_options"] = {"model": self.model}
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        http_request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                http_request, timeout=self.timeout_seconds
            ) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"HTTP {exc.code} from generation adapter: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"generation adapter is unreachable: {exc.reason}") from exc

        try:
            decoded = json.loads(raw)
        except ValueError as exc:
            raise ValueError("generation adapter returned invalid JSON") from exc
        return GenerationCandidate.from_mapping(_candidate_mapping(decoded))
