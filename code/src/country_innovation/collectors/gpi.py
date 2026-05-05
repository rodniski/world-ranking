"""Global Peace Index 2025 (Institute for Economics & Peace).

Wikipedia em `Global_Peace_Index` mantem a tabela do ranking mais recente
com colunas `Rank, Country, Score, Change`.  Score: 1.0-5.0, **menor eh
melhor** (mais pacifico).  Direction = -1 vai pro IndicatorMeta.
"""

from __future__ import annotations

import io
import logging
import re

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://en.wikipedia.org/api/rest_v1/page/html/Global_Peace_Index"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}
EDITION_HINT_RE = re.compile(r"\bGPI\s+(20\d{2})\b|\bGlobal\s+Peace\s+Index\s+(20\d{2})\b")


class GPI(Collector):
    source_id = "GPI-2025"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text
        tables = pd.read_html(io.StringIO(html), flavor="lxml")

        year = _detect_latest_year(html)
        df = _pick_gpi_table(tables)
        if df is None:
            raise RuntimeError("GPI/Wikipedia: tabela Rank/Country/Score nao encontrada")

        log.info("GPI: ano = %d, %d paises", year, len(df))
        out = pd.DataFrame(
            {
                "country": df["Country"].astype(str).str.strip(),
                "value": pd.to_numeric(df["Score"], errors="coerce"),
                "indicator_id": "gpi_score",
                "year": year,
            }
        ).dropna(subset=["value"])

        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]


def _detect_latest_year(html: str) -> int:
    years: list[int] = []
    for m in EDITION_HINT_RE.finditer(html):
        for grp in m.groups():
            if grp:
                years.append(int(grp))
    return max(years) if years else 0


def _pick_gpi_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    for t in tables:
        cols = [str(c) for c in t.columns]
        if {"Rank", "Country", "Score"}.issubset(cols) and t.shape[0] >= 100:
            return t
    return None
