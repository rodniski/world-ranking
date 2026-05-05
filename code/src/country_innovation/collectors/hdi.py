"""UNDP — Human Development Index (HDR 2025, dados ate 2023).

URL: https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv

CSV em formato wide com 1100+ colunas: ISO3 + nome + region + hdi_1990,
hdi_1991, ..., hdi_2023 + outros indicadores compostos.  O encoding eh
latin-1 (UNDP usa byte ranges nao-UTF8 em alguns nomes de pais).

Pegamos a coluna `hdi_<ultimo_ano>` (HDR 2025 = 2023) e mapeamos pra
schema LONG. Sub-indicadores (life expectancy, schooling) ficam fora
nesta versao — adicionar se aggregator precisar.
"""

from __future__ import annotations

import io
import logging

import pandas as pd
import requests

from country_innovation.collectors.base import Collector
from country_innovation.countries import is_in_scope

log = logging.getLogger(__name__)

URL = (
    "https://hdr.undp.org/sites/default/files/2025_HDR/"
    "HDR25_Composite_indices_complete_time_series.csv"
)
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}


class HDI(Collector):
    source_id = "HDI-2025"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        text = r.content.decode("latin-1")
        df = pd.read_csv(io.StringIO(text))

        latest_col, latest_year = _latest_hdi_column(df)
        log.info("HDI: coluna mais recente = %s (ano %d)", latest_col, latest_year)

        out = pd.DataFrame(
            {
                "iso3": df["iso3"].astype(str).str.strip(),
                "value": pd.to_numeric(df[latest_col], errors="coerce"),
                "indicator_id": "hdi_overall",
                "year": latest_year,
            }
        ).dropna(subset=["value"])

        out = out[out["iso3"].apply(is_in_scope)].reset_index(drop=True)
        return out[["iso3", "indicator_id", "value", "year"]]


def _latest_hdi_column(df: pd.DataFrame) -> tuple[str, int]:
    """Acha a coluna `hdi_<ano>` mais recente (ignora `hdi_rank_*`)."""
    hdi_year_cols = [c for c in df.columns if c.startswith("hdi_") and c[4:].isdigit()]
    if not hdi_year_cols:
        raise RuntimeError(
            f"HDI: nenhuma coluna hdi_<ano> encontrada em {df.columns.tolist()[:20]}"
        )
    latest = max(hdi_year_cols, key=lambda c: int(c[4:]))
    return latest, int(latest[4:])
