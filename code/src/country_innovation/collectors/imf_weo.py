"""IMF — World Economic Outlook (April 2025).

API: https://www.imf.org/external/datamapper/api/v1/{indicator}
Doc: https://www.imf.org/en/Publications/WEO

Cada indicador devolve `{values: {INDICATOR: {ISO3: {ano_str: valor}}}}`.
ISO3 ja vem direto, entao pulamos `normalize_iso3` e filtramos so por escopo.

Importante: a serie inclui projecoes pra anos futuros (2025+).  Pegamos
o ano mais recente com cobertura forte (>=150 paises) — pode ser
projecao IMF, mas eh o melhor conhecimento atual disponivel.
"""

from __future__ import annotations

import datetime as dt
import logging

import pandas as pd
import requests

from country_innovation.collectors.base import Collector
from country_innovation.countries import is_in_scope

log = logging.getLogger(__name__)

INDICATORS: dict[str, str] = {
    "imf_gdp_pcap_usd": "NGDPDPC",  # GDP per capita, current USD
    "imf_inflation": "PCPIPCH",  # Inflation, average consumer prices (% change)
    "imf_unemployment": "LUR",  # Unemployment rate (% of labor force)
    "imf_govt_debt_gdp": "GGXWDG_NGDP",  # Government gross debt (% of GDP)
}
COVERAGE_THRESHOLD = 150


class IMFWEO(Collector):
    source_id = "IMF-WEO-2025"

    def fetch(self) -> pd.DataFrame:
        frames = [
            self._fetch_indicator(indicator_id, imf_code)
            for indicator_id, imf_code in INDICATORS.items()
        ]
        df = pd.concat(frames, ignore_index=True)
        df = df[df["iso3"].apply(is_in_scope)].reset_index(drop=True)
        return df[["iso3", "indicator_id", "value", "year"]]

    @staticmethod
    def _fetch_indicator(indicator_id: str, imf_code: str) -> pd.DataFrame:
        url = f"https://www.imf.org/external/datamapper/api/v1/{imf_code}"
        log.info("GET %s", url)
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        payload = r.json()
        country_data = payload.get("values", {}).get(imf_code, {})
        if not country_data:
            raise RuntimeError(f"IMF {imf_code}: payload sem dados ({payload!r})")

        rows: list[dict] = []
        for iso3, year_values in country_data.items():
            for year_str, raw_val in year_values.items():
                value = _coerce_float(raw_val)
                if value is None:
                    continue
                rows.append(
                    {
                        "iso3": iso3,
                        "year": int(year_str),
                        "value": value,
                        "indicator_id": indicator_id,
                    }
                )

        df = pd.DataFrame(rows)
        # IMF inclui projecoes ate ~5 anos a frente; cortar pra evitar pegar
        # projecao distante como "ano valido". current_year - 1 garante que
        # estamos no ultimo ano com publicacao ja consolidada.
        max_actual_year = dt.date.today().year - 1
        df = df[df["year"] <= max_actual_year]
        cov = df.groupby("year")["iso3"].nunique().sort_index(ascending=False)
        year = next((y for y, n in cov.items() if n >= COVERAGE_THRESHOLD), cov.index[0])
        log.info("[%s] ano = %d (cobertura = %d)", indicator_id, year, cov.loc[year])
        return df[df["year"] == year]


def _coerce_float(val: object) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
