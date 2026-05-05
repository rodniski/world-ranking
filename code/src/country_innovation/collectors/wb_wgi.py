"""World Bank — Worldwide Governance Indicators (WGI).

Doc: https://www.worldbank.org/en/publication/worldwide-governance-indicators

Mesma API JSON do `wb_ppp.py` (sem chave). Pegamos os 6 indicadores classicos
do WGI; cada um vira uma `indicator_id` distinta no schema LONG, deixando o
aggregator decidir como combinar dentro da dimensao MACRO.

Valores ficam em `[-2.5, +2.5]` (WGI sempre direction=+1).
"""

from __future__ import annotations

import logging

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

INDICATORS: dict[str, str] = {
    "wgi_va": "GOV_WGI_VA.EST",  # Voice and Accountability
    "wgi_pv": "GOV_WGI_PV.EST",  # Political Stability and Absence of Violence/Terrorism
    "wgi_ge": "GOV_WGI_GE.EST",  # Government Effectiveness
    "wgi_rq": "GOV_WGI_RQ.EST",  # Regulatory Quality
    "wgi_rl": "GOV_WGI_RL.EST",  # Rule of Law
    "wgi_cc": "GOV_WGI_CC.EST",  # Control of Corruption
}
COVERAGE_THRESHOLD = 150


class WorldBankWGI(Collector):
    source_id = "WB-WGI"

    def fetch(self) -> pd.DataFrame:
        frames = [
            self._fetch_indicator(indicator_id, wb_code)
            for indicator_id, wb_code in INDICATORS.items()
        ]
        df = pd.concat(frames, ignore_index=True)
        df = self.normalize_iso3(df, name_col="country")
        return df[["iso3", "indicator_id", "value", "year"]]

    @staticmethod
    def _fetch_indicator(indicator_id: str, wb_code: str) -> pd.DataFrame:
        url = (
            f"https://api.worldbank.org/v2/country/all/indicator/{wb_code}"
            "?format=json&source=3&per_page=20000"
        )
        log.info("GET %s", url)
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        payload = r.json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError(f"resposta inesperada WB ({wb_code}): {payload!r}")

        df = pd.DataFrame(
            [
                {
                    "country": row["country"]["value"],
                    "value": row["value"],
                    "year": int(row["date"]),
                    "indicator_id": indicator_id,
                }
                for row in payload[1]
            ]
        ).dropna(subset=["value"])

        cov = df.groupby("year")["country"].nunique().sort_index(ascending=False)
        year = next((y for y, n in cov.items() if n >= COVERAGE_THRESHOLD), cov.index[0])
        log.info("[%s] ano = %d (cobertura = %d)", indicator_id, year, cov.loc[year])
        return df[df["year"] == year]
