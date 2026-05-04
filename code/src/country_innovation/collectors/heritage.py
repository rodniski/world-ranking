"""Heritage Foundation — Index of Economic Freedom 2026.

`economicfreedom.heritage.org` esta protegido por Cloudflare com bloqueio
TLS-fingerprint que rejeita `requests`/`urllib`/`curl` puros (HTTP 403 em
qualquer endpoint, mesmo na home).  Bypass exigiria `curl_cffi`/Playwright,
que sao anti-pattern do projeto.

Solucao: usar a Wikipedia como proxy.  A pagina
`List_of_countries_by_economic_freedom` mantem a tabela oficial do IEF 2026
com colunas `Country, Score, Change` e sai pelo `api/rest_v1/page/html/...`
em HTML estavel, sem JS.
"""

from __future__ import annotations

import io
import logging

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://en.wikipedia.org/api/rest_v1/page/html/List_of_countries_by_economic_freedom"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}
IEF_YEAR = 2026


class Heritage(Collector):
    source_id = "IEF-2026"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()

        tables = pd.read_html(io.StringIO(r.text), flavor="lxml")
        df = self._pick_ief_table(tables)
        if df is None:
            raise RuntimeError(
                "Heritage/Wikipedia: tabela IEF 2026 nao encontrada; "
                f"{len(tables)} tabelas vistas, shapes={[t.shape for t in tables]}"
            )

        out = pd.DataFrame(
            {
                "country": df["Country"].astype(str).str.strip(),
                "value": pd.to_numeric(df["Score"], errors="coerce"),
                "indicator_id": "ief_overall",
                "year": IEF_YEAR,
            }
        ).dropna(subset=["value"])

        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]

    @staticmethod
    def _pick_ief_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
        """Wikipedia lista varias edicoes do IEF; pegamos a mais recente
        (a Heritage 2026 — ultima tabela com schema Country/Score/Change)."""
        candidates = [t for t in tables if list(t.columns)[:3] == ["Country", "Score", "Change"]]
        return candidates[-1] if candidates else None
