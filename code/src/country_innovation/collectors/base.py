"""Classe base para todos os collectors.

Contrato: cada subclasse implementa `fetch()` que devolve um DataFrame em
formato long com as colunas de schema.LONG_COLUMNS.  A classe base cuida de:
- normalizacao de nomes de pais pra ISO3
- filtragem por SCOPE_BLACKLIST
- gravacao em data/raw/<source_id>.csv (canonico)
- upload de manifest + snapshot em Convex (observabilidade, best-effort)
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from country_innovation.convex_client import ScrapeRow, record_run
from country_innovation.countries import is_in_scope, to_iso3
from country_innovation.schema import LONG_COLUMNS

log = logging.getLogger(__name__)


def _now_ms() -> int:
    return int(time.time() * 1000)


class Collector(ABC):
    source_id: str  # ex: "GII-2025"
    raw_dir: Path = Path("data/raw")

    def __init__(self, raw_dir: Path | None = None):
        if raw_dir is not None:
            self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Devolve DataFrame em formato long.  Pode usar nomes de pais humanos
        em vez de ISO3 — a normalizacao acontece em `run()`.
        """
        ...

    def normalize_iso3(self, df: pd.DataFrame, name_col: str = "country") -> pd.DataFrame:
        """Adiciona coluna iso3 e descarta linhas que nao mapearam."""
        df = df.copy()
        df["iso3"] = df[name_col].map(to_iso3)
        unmapped = df[df["iso3"].isna()][name_col].unique()
        if len(unmapped) > 0:
            log.warning(
                "%s: %d nomes nao mapeados → %s",
                self.source_id,
                len(unmapped),
                list(unmapped[:10]),
            )
        df = df.dropna(subset=["iso3"])
        df = df[df["iso3"].apply(is_in_scope)]
        return df

    def run(self) -> pd.DataFrame:
        """Pipeline completo: fetch → normalize → save → upload Convex."""
        started = _now_ms()
        try:
            raw = self._fetch_validated()
        except Exception as exc:
            self._upload_failure(started, exc)
            raise
        self._save_csv(raw)
        self._upload_success(raw, started)
        return raw

    def _fetch_validated(self) -> pd.DataFrame:
        log.info("[%s] fetch...", self.source_id)
        raw = self.fetch()
        if raw.empty:
            raise RuntimeError(f"[{self.source_id}] fetch devolveu DataFrame vazio")
        raw["source_id"] = self.source_id
        missing = set(LONG_COLUMNS) - set(raw.columns)
        if missing:
            raise ValueError(f"[{self.source_id}] colunas faltando: {missing}")
        return raw[LONG_COLUMNS]

    def _save_csv(self, raw: pd.DataFrame) -> None:
        out = self.raw_dir / f"{self.source_id}.csv"
        raw.to_csv(out, index=False)
        log.info(
            "[%s] %d linhas, %d paises → %s",
            self.source_id,
            len(raw),
            raw["iso3"].nunique(),
            out,
        )

    def _upload_success(self, raw: pd.DataFrame, started_ms: int) -> None:
        rows: list[ScrapeRow] = [
            {
                "iso3": str(r.iso3),
                "indicator_id": str(r.indicator_id),
                "value": float(r.value),
                "year": int(r.year),
            }
            for r in raw.itertuples(index=False)
        ]
        record_run(
            source_id=self.source_id,
            started_at_ms=started_ms,
            finished_at_ms=_now_ms(),
            status="ok",
            rows=rows,
        )

    def _upload_failure(self, started_ms: int, exc: Exception) -> None:
        record_run(
            source_id=self.source_id,
            started_at_ms=started_ms,
            finished_at_ms=_now_ms(),
            status="failed",
            rows=[],
            error=str(exc),
        )
