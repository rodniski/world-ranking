"""WIPO — Global Innovation Index 2025.

URL canônica (confirmada pelo usuário):
https://www.wipo.int/web-publications/global-innovation-index-2025/en/gii-2025-results.html

A página contém uma tabela com Score + Rank + Income group + Region.  Mesma
estratégia da Heritage: pandas.read_html primeiro, BS4 manual como fallback.
"""
from __future__ import annotations

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = (
    "https://www.wipo.int/web-publications/global-innovation-index-2025/en/"
    "gii-2025-results.html"
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


class GII(Collector):
    source_id = "GII-2025"

    def fetch(self) -> pd.DataFrame:
        log.info("GET %s", URL)
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text

        try:
            tables = pd.read_html(html)
        except ValueError:
            tables = []

        df = None
        for t in tables:
            cols = " ".join(str(c).lower() for c in t.columns)
            if t.shape[0] >= 100 and ("economy" in cols or "country" in cols) \
                    and ("score" in cols or "rank" in cols):
                df = t
                break

        if df is None:
            df = self._parse_manual(html)
        if df is None or df.empty:
            raise RuntimeError(
                "GII: tabela não encontrada — provável que seja renderizada "
                "client-side ou esteja em iframe."
            )

        df.columns = [str(c).strip() for c in df.columns]
        country_col = self._find_col(df, ["economy", "country"])
        score_col = self._find_col(df, ["score"])
        if country_col is None or score_col is None:
            raise RuntimeError(
                f"GII: colunas country/score não localizadas; "
                f"colunas vistas: {df.columns.tolist()}"
            )

        out = pd.DataFrame({
            "country": df[country_col].astype(str).str.strip(),
            "value": pd.to_numeric(df[score_col], errors="coerce"),
            "indicator_id": "gii_overall",
            "year": 2025,
        }).dropna(subset=["value"])

        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]

    # ------------------------------------------------------------------
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
        for t in soup.find_all("table"):
            rows = t.find_all("tr")
            if len(rows) > 100:
                header = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
                data = []
                for tr in rows[1:]:
                    cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
                    if len(cells) == len(header):
                        data.append(cells)
                if data:
                    return pd.DataFrame(data, columns=header)
        return None
