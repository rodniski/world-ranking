"""Heritage Foundation — Index of Economic Freedom 2026.

URL canônica (confirmada pelo usuário): a página `all-country-scores` traz a
tabela completa em HTML.  Estratégia:

1. `pandas.read_html` — pega tudo que parece tabela.
2. Se vier vazia, tentar fallback baixando HTML e parseando manualmente.
3. Se ambos falharem, sinalizar pro pipeline pular essa fonte.
"""
from __future__ import annotations

import io
import logging
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://economicfreedom.heritage.org/pages/all-country-scores"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.heritage.org/index/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class Heritage(Collector):
    source_id = "IEF-2026"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text

        # Tentativa 1 — pandas
        tables = []
        try:
            tables = pd.read_html(io.StringIO(html), flavor="lxml")
        except ValueError:
            tables = []

        df = self._pick_country_table(tables)

        # Tentativa 2 — parse manual da maior tabela do BS4
        if df is None:
            df = self._parse_manual(html)

        if df is None or df.empty:
            raise RuntimeError(
                "Heritage: nenhuma tabela reconhecível encontrada na página.  "
                "Provável que o conteúdo seja renderizado por JS — investigar."
            )

        # Esperamos colunas tipo: Country, Overall Score (com possíveis sufixos
        # de pilares).  Padronizamos.
        df.columns = [str(c).strip() for c in df.columns]
        country_col = self._find_col(df, ["country", "name", "economy"])
        score_col = self._find_col(df, ["overall", "score", "ief"])
        if country_col is None or score_col is None:
            raise RuntimeError(
                f"Heritage: colunas country/score não localizadas; "
                f"colunas vistas: {df.columns.tolist()}"
            )

        out = pd.DataFrame({
            "country": df[country_col].astype(str).str.strip(),
            "value": pd.to_numeric(df[score_col], errors="coerce"),
            "indicator_id": "ief_overall",
            "year": 2026,
        }).dropna(subset=["value"])

        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _pick_country_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
        for t in tables:
            if t.shape[0] >= 100:  # esperamos ~184 países
                cols = " ".join(str(c).lower() for c in t.columns)
                if "country" in cols or "economy" in cols:
                    return t
        return None

    @staticmethod
    def _find_col(df: pd.DataFrame, hints: list[str]) -> str | None:
        for c in df.columns:
            cl = str(c).lower()
            if any(h in cl for h in hints):
                return c
        return None

    @staticmethod
    def _parse_manual(html: str) -> pd.DataFrame | None:
        soup = BeautifulSoup(html, "lxml")
        candidates = soup.find_all("table")
        best = None
        for t in candidates:
            rows = t.find_all("tr")
            if len(rows) > 100:
                best = t
                break
        if best is None:
            return None
        data = []
        rows = best.find_all("tr")
        header_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
        for tr in rows[1:]:
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if len(cells) == len(header_cells):
                data.append(cells)
        if not data:
            return None
        return pd.DataFrame(data, columns=header_cells)
