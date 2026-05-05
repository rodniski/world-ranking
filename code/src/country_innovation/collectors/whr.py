"""World Happiness Report — versao mais recente disponivel na Wikipedia.

A pagina `World_Happiness_Report` empilha tabelas de varios anos.  Cada
tabela com colunas exatas `Overall rank, Country or region, Score, ...`
representa um ano.  A primeira no DOM eh a mais recente.

Indicador: `whr_score` (0-10, direction = +1).
"""

from __future__ import annotations

import io
import logging
import re

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://en.wikipedia.org/api/rest_v1/page/html/World_Happiness_Report"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}
WHR_REQUIRED_COLS = ("Overall rank", "Country or region", "Score")
EDITION_HINT_RE = re.compile(r"World\s+Happiness\s+Report\s+(20\d{2})", re.IGNORECASE)


class WHR(Collector):
    source_id = "WHR-2025"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text
        tables = pd.read_html(io.StringIO(html), flavor="lxml")

        year = _detect_latest_year(html)
        df = _pick_first_score_table(tables)
        if df is None:
            raise RuntimeError(
                "WHR/Wikipedia: nenhuma tabela com Overall rank/Country or region/Score"
            )

        log.info("WHR: ano = %d, %d paises", year, len(df))
        out = pd.DataFrame(
            {
                "country": df["Country or region"].astype(str).str.strip(),
                "value": pd.to_numeric(df["Score"], errors="coerce"),
                "indicator_id": "whr_score",
                "year": year,
            }
        ).dropna(subset=["value"])

        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]


def _detect_latest_year(html: str) -> int:
    """Acha o ano mais recente mencionado na pagina (ex: 'World Happiness Report 2025')."""
    years = [int(m.group(1)) for m in EDITION_HINT_RE.finditer(html)]
    return max(years) if years else 0


def _pick_first_score_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    for t in tables:
        cols = [str(c) for c in t.columns]
        if all(req in cols for req in WHR_REQUIRED_COLS) and t.shape[0] >= 100:
            return t
    return None
