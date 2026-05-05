"""Numbeo Cost of Living rankings (auto-atualizado).

URL canonica: `numbeo.com/cost-of-living/rankings_by_country.jsp`
A pagina renderiza a tabela de paises em HTML (sem JS) e nao bloqueia
requests com User-Agent decente.

Coletamos 2 indicadores do mesmo source:
  - `numbeo_col_index` (Cost of Living Index, NYC=100, direction = -1)
  - `numbeo_lpp_index` (Local Purchasing Power Index, NYC=100, direction = +1)

Numbeo nao versiona explicitamente ano da publicacao no HTML; usamos
o ano corrente como referencia.
"""

from __future__ import annotations

import datetime as dt
import io
import logging

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://www.numbeo.com/cost-of-living/rankings_by_country.jsp"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}


class Numbeo(Collector):
    source_id = "NUMBEO"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        tables = pd.read_html(io.StringIO(r.text), flavor="lxml")
        df = _pick_numbeo_table(tables)
        if df is None:
            raise RuntimeError("Numbeo: tabela de paises nao encontrada")

        year = dt.date.today().year
        log.info("Numbeo: ano = %d, %d paises", year, len(df))
        return self._build_long(df, year)

    def _build_long(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        """Stack 2 indicadores (`col_index`, `lpp_index`) em formato long."""
        countries = df["Country"].astype(str).str.strip()
        col_long = pd.DataFrame(
            {
                "country": countries,
                "value": pd.to_numeric(df["Cost of Living Index"], errors="coerce"),
                "indicator_id": "numbeo_col_index",
                "year": year,
            }
        )
        lpp_long = pd.DataFrame(
            {
                "country": countries,
                "value": pd.to_numeric(df["Local Purchasing Power Index"], errors="coerce"),
                "indicator_id": "numbeo_lpp_index",
                "year": year,
            }
        )
        out = pd.concat([col_long, lpp_long], ignore_index=True).dropna(subset=["value"])
        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]


def _pick_numbeo_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    required = {"Country", "Cost of Living Index", "Local Purchasing Power Index"}
    for t in tables:
        cols = {str(c) for c in t.columns}
        if required.issubset(cols) and t.shape[0] >= 50:
            return t
    return None
