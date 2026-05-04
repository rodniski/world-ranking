"""WIPO — Global Innovation Index 2025.

A pagina oficial do GII 2025 nao expoe a tabela em HTML — os rankings sao
embeddados via charts Datawrapper (datawrapper.dwcdn.net).  O endpoint
`dataset.csv` do chart `Pv2kB` v9 ja vem com ISO3 e `GII score` para 138
economias.  E a fonte de dados que o proprio site usa.
"""
from __future__ import annotations

import io
import logging

import pandas as pd
import requests

from country_innovation.collectors.base import Collector
from country_innovation.countries import is_in_scope

log = logging.getLogger(__name__)

URL = "https://datawrapper.dwcdn.net/Pv2kB/9/dataset.csv"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
}


class GII(Collector):
    source_id = "GII-2025"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        # Datawrapper publica "Hong Kong, China" sem aspas — quebra o parser CSV.
        text = r.text.replace("Hong Kong, China", "Hong Kong (China)")
        df = pd.read_csv(io.StringIO(text))

        if "ISO3" not in df.columns or "GII score" not in df.columns:
            raise RuntimeError(
                f"GII: schema inesperado no Datawrapper; colunas: {df.columns.tolist()}"
            )

        out = pd.DataFrame({
            "iso3": df["ISO3"].astype(str).str.strip(),
            "value": pd.to_numeric(df["GII score"], errors="coerce"),
            "indicator_id": "gii_overall",
            "year": 2025,
        }).dropna(subset=["value"])

        out = out[out["iso3"].apply(is_in_scope)].reset_index(drop=True)
        return out[["iso3", "indicator_id", "value", "year"]]
