"""Top marginal individual income tax — substituicao para KPMG/OECD-TAXING-WAGES.

KPMG e OECD nao tem CSV publico facil; KPMG-TAX paywall + scrape complexo,
OECD bloqueia `requests` (Cloudflare).  A pagina Wikipedia
`List_of_countries_by_tax_rates` agrega taxas oficiais (corporate, individual,
VAT, etc.) por pais e e mantida pelos editores.

Pegamos a coluna `Individual income / Highest` (top marginal income tax).
Valores vem como `20%[3]`, `19–26%[9]` etc — parser extrai o numero mais
alto (range take-last) e descarta footnotes.

Direction = -1 (mais imposto = pior pra net pay) — vai pro IndicatorMeta.
"""

from __future__ import annotations

import datetime as dt
import io
import logging
import re

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://en.wikipedia.org/api/rest_v1/page/html/List_of_countries_by_tax_rates"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}
FOOTNOTE_RE = re.compile(r"\[\d+\]")
PCT_NUMBER_RE = re.compile(r"(\d+(?:\.\d+)?)")


class TaxRatesWiki(Collector):
    source_id = "TAX-RATES-WIKI"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        tables = pd.read_html(io.StringIO(r.text), flavor="lxml")

        df = _pick_tax_table(tables)
        if df is None:
            raise RuntimeError("TaxRatesWiki: tabela de taxas nao encontrada")

        country_col = ("Tax jurisdiction", "Tax jurisdiction")
        income_col = ("Individual income", "Highest")
        if country_col not in df.columns or income_col not in df.columns:
            raise RuntimeError(f"TaxRatesWiki: colunas esperadas ausentes em {df.columns.tolist()}")

        year = dt.date.today().year
        log.info("TaxRatesWiki: %d jurisdicoes, ano = %d", len(df), year)

        out = pd.DataFrame(
            {
                "country": df[country_col].astype(str).str.strip(),
                "value": df[income_col].apply(_parse_pct),
                "indicator_id": "top_marginal_income_tax",
                "year": year,
            }
        ).dropna(subset=["value"])

        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]


def _parse_pct(raw: object) -> float | None:
    """Extrai a aliquota top marginal de strings tipo:

    - `20%[3]`                                 -> 20.0
    - `19-26%[9]`                              -> 26.0  (range take-max)
    - `45% (+ 39.2% social security...)`       -> 45.0  (ignora parenteses)
    - `48% to 54%[263] (depending...)`         -> 54.0  (range)
    - `50.3% California (37% (federal)...)`    -> 50.3

    Estrategia: corta footnotes, pega o trecho ANTES do primeiro
    parenteses (onde fica a aliquota headline) e devolve o maior numero
    valido [0,100] dali — assim ranges com hifen ou "to" pegam o teto.
    """
    if not isinstance(raw, str):
        return None
    cleaned = FOOTNOTE_RE.sub("", raw)
    headline = cleaned.split("(", 1)[0]
    nums = [float(n) for n in PCT_NUMBER_RE.findall(headline)]
    valid = [n for n in nums if 0 <= n <= 100]
    return max(valid) if valid else None


def _pick_tax_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    for t in tables:
        if t.shape[0] >= 100 and isinstance(t.columns, pd.MultiIndex):
            return t
    return None
