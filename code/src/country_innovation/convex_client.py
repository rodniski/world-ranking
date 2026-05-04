"""Cliente HTTP minimal para gravar runs e scrapes no Convex.

Le `CONVEX_URL` do ambiente. Se ausente, vira no-op silencioso — o
pipeline continua funcionando sem Convex; ele eh observabilidade,
nao fonte canonica (essa eh `data/raw/*.csv`).
"""

from __future__ import annotations

import logging
import os
from typing import Any, TypedDict

import requests

log = logging.getLogger(__name__)

ENV_VAR = "CONVEX_URL"
TIMEOUT_SECS = 30


class ScrapeRow(TypedDict):
    iso3: str
    indicator_id: str
    value: float
    year: int


def _convex_url() -> str | None:
    url = os.environ.get(ENV_VAR)
    return url.rstrip("/") if url else None


def record_run(
    *,
    source_id: str,
    started_at_ms: int,
    finished_at_ms: int,
    status: str,
    rows: list[ScrapeRow],
    error: str | None = None,
) -> str | None:
    """Grava 1 run + N scrapes (atomico no servidor) e devolve `run_id`.

    Retorna `None` em qualquer falha — o pipeline NAO deve quebrar
    se Convex estiver offline.
    """
    url = _convex_url()
    if not url:
        log.info("[%s] %s ausente, pulando upload Convex", source_id, ENV_VAR)
        return None

    args: dict[str, Any] = {
        "source_id": source_id,
        "started_at": started_at_ms,
        "finished_at": finished_at_ms,
        "status": status,
        "rows": rows,
    }
    if error is not None:
        args["error"] = error

    try:
        r = requests.post(
            f"{url}/api/mutation",
            json={"path": "runs:record", "args": args, "format": "json"},
            timeout=TIMEOUT_SECS,
        )
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as exc:
        log.warning("[%s] upload Convex falhou: %s", source_id, exc)
        return None

    if data.get("status") != "success":
        log.warning("[%s] Convex devolveu erro: %s", source_id, data)
        return None
    return data.get("value")
