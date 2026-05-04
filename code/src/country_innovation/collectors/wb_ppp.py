"""World Bank — GNI per capita PPP (current international $).

Indicador: NY.GNP.PCAP.PP.CD
Doc: https://data.worldbank.org/indicator/NY.GNP.PCAP.PP.CD

API JSON pública, sem chave.  Pegamos o ano mais recente com cobertura ≥150
países pra evitar usar um ano em que o WB ainda está revisando metade dos
dados.
"""
from __future__ import annotations

import logging

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

INDICATOR = "NY.GNP.PCAP.PP.CD"
URL = (
    f"https://api.worldbank.org/v2/country/all/indicator/{INDICATOR}"
    "?format=json&per_page=20000"
)


class WorldBankPPP(Collector):
    source_id = "WB-PPP"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, timeout=30)
        r.raise_for_status()
        payload = r.json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError(f"resposta inesperada do WB: {payload!r}")

        rows = payload[1]  # payload[0] é metadata
        df = pd.DataFrame([
            {
                "country": row["country"]["value"],
                "iso3_wb": row["countryiso3code"],   # WB já dá ISO3, conferimos
                "value": row["value"],
                "year": int(row["date"]),
                "indicator_id": "wb_gni_pcap_ppp",
            }
            for row in rows
        ])
        df = df.dropna(subset=["value"])

        # Pegar o ano mais recente com cobertura forte (>=150 países).
        cov = df.groupby("year")["iso3_wb"].nunique().sort_index(ascending=False)
        chosen_year = next((y for y, n in cov.items() if n >= 150), cov.index[0])
        log.info("WB: ano escolhido = %d (cobertura = %d países)",
                 chosen_year, cov.loc[chosen_year])
        df = df[df["year"] == chosen_year]

        # WB já fornece ISO3 — usamos direto e descartamos agregados regionais
        # (que vêm com códigos tipo "WLD", "EAS", "OED" etc.).
        df = self.normalize_iso3(df, name_col="country")
        return df[["iso3", "indicator_id", "value", "year"]]
