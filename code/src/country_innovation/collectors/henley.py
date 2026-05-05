"""Henley Passport Index 2026.

Henley publica scores propietarios mas Wikipedia mantem o ranking oficial
em `Henley_Passport_Index` com tabelas por ano.  Pegamos a tabela mais
recente cujo header comeca com "<ano> rank" — geralmente sao varias
edicoes empilhadas, a primeira eh a mais nova.

Indicador: numero de destinos visa-free para o passaporte de cada pais.
Direction = +1 (mais destinos = melhor mobilidade).
"""

from __future__ import annotations

import io
import logging
import re

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://en.wikipedia.org/api/rest_v1/page/html/Henley_Passport_Index"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}
YEAR_RE = re.compile(r"^(20\d{2})\s+rank")


class HenleyPassport(Collector):
    source_id = "HENLEY-2026"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        tables = pd.read_html(io.StringIO(r.text), flavor="lxml")

        df, year = _pick_latest_henley(tables)
        if df is None:
            raise RuntimeError(
                "Henley/Wikipedia: nenhuma tabela com '<ano> rank' / "
                "'Passport issuing country' / 'Visa-free destinations' encontrada"
            )

        log.info("HENLEY: usando tabela %d (%d paises)", year, len(df))
        out = pd.DataFrame(
            {
                "country": df["Passport issuing country"].astype(str).str.strip(),
                "value": pd.to_numeric(df["Visa-free destinations"], errors="coerce"),
                "indicator_id": "henley_visa_free",
                "year": year,
            }
        ).dropna(subset=["value"])

        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]


def _pick_latest_henley(
    tables: list[pd.DataFrame],
) -> tuple[pd.DataFrame | None, int]:
    """Acha a primeira tabela cujo header bate `<ano> rank` (a mais recente)."""
    for t in tables:
        cols = [str(c) for c in t.columns]
        if len(cols) < 3:
            continue
        m = YEAR_RE.match(cols[0])
        if not m:
            continue
        if "Passport issuing country" not in cols or "Visa-free destinations" not in cols:
            continue
        return t, int(m.group(1))
    return None, 0
