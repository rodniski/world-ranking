"""Classe base para todos os collectors.

Contrato: cada subclasse implementa `fetch()` que devolve um DataFrame em
formato long com as colunas de schema.LONG_COLUMNS.  A classe base cuida de:
- normalização de nomes de país pra ISO3
- filtragem por SCOPE_BLACKLIST
- gravação em data/raw/<source_id>.csv
- log de cobertura (% dos países do escopo cobertos)
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from country_innovation.countries import is_in_scope, to_iso3
from country_innovation.schema import LONG_COLUMNS

log = logging.getLogger(__name__)


class Collector(ABC):
    source_id: str            # ex: "GII-2025"
    raw_dir: Path = Path("data/raw")

    def __init__(self, raw_dir: Path | None = None):
        if raw_dir is not None:
            self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Devolve DataFrame em formato long.  Pode usar nomes de país humanos
        em vez de ISO3 — a normalização acontece em `run()`.
        """
        ...

    def normalize_iso3(self, df: pd.DataFrame, name_col: str = "country") -> pd.DataFrame:
        """Adiciona coluna iso3 e descarta linhas que não mapearam."""
        df = df.copy()
        df["iso3"] = df[name_col].map(to_iso3)
        unmapped = df[df["iso3"].isna()][name_col].unique()
        if len(unmapped) > 0:
            log.warning("%s: %d nomes não mapeados → %s",
                        self.source_id, len(unmapped), list(unmapped[:10]))
        df = df.dropna(subset=["iso3"])
        df = df[df["iso3"].apply(is_in_scope)]
        return df

    def run(self) -> pd.DataFrame:
        """Pipeline completo: fetch → normalize → save → log."""
        log.info("[%s] fetch...", self.source_id)
        raw = self.fetch()
        if raw.empty:
            raise RuntimeError(f"[{self.source_id}] fetch devolveu DataFrame vazio")

        # Garantir source_id presente
        raw["source_id"] = self.source_id

        # Schema check
        missing = set(LONG_COLUMNS) - set(raw.columns)
        if missing:
            raise ValueError(f"[{self.source_id}] colunas faltando: {missing}")

        # Save
        out = self.raw_dir / f"{self.source_id}.csv"
        raw[LONG_COLUMNS].to_csv(out, index=False)
        n_countries = raw["iso3"].nunique()
        n_rows = len(raw)
        log.info("[%s] %d linhas, %d países → %s", self.source_id, n_rows, n_countries, out)
        return raw[LONG_COLUMNS]
