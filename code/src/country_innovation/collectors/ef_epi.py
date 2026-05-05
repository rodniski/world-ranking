"""EF English Proficiency Index — edicao mais recente (Education First).

Wikipedia em `EF_English_Proficiency_Index` mantem a tabela mais recente
com colunas `Country or region, Score, Proficiency band`.

Indicador: `ef_epi_score` (0-700+ aproximadamente, direction = +1).
Util pro VISA porque dominio do ingles eh proxy de empregabilidade
internacional pro SWE BR (que ja tende a falar ingles tecnico decente).
"""

from __future__ import annotations

import io
import logging
import re

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://en.wikipedia.org/api/rest_v1/page/html/EF_English_Proficiency_Index"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}
EDITION_HINT_RE = re.compile(
    r"EF\s+EPI\s+(20\d{2})|EF\s+English\s+Proficiency.*?(20\d{2})", re.IGNORECASE
)


class EFEPIIndex(Collector):
    source_id = "EF-EPI-2025"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text
        tables = pd.read_html(io.StringIO(html), flavor="lxml")

        year = _detect_latest_year(html)
        df = _pick_ef_epi_table(tables)
        if df is None:
            raise RuntimeError(
                "EF-EPI/Wikipedia: tabela Country/Score/Proficiency band nao encontrada"
            )

        log.info("EF-EPI: ano = %d, %d paises", year, len(df))
        out = pd.DataFrame(
            {
                "country": df["Country or region"].astype(str).str.strip(),
                "value": pd.to_numeric(df["Score"], errors="coerce"),
                "indicator_id": "ef_epi_score",
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


def _pick_ef_epi_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    for t in tables:
        cols = [str(c) for c in t.columns]
        if {"Country or region", "Score", "Proficiency band"}.issubset(cols) and t.shape[0] >= 50:
            return t
    return None
