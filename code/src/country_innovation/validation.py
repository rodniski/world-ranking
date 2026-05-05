"""Sanity checks aplicados ao ranking final (metodologia §8).

Pipeline FALHA se:
    - top 10 nao tem >= 5 OECD (sinal de bug de normalizacao)
    - Brasil fora de [50, 110] (calibracao)
    - score com NaN ou fora de [0, 100]
"""

from __future__ import annotations

import logging

import pandas as pd

log = logging.getLogger(__name__)

# OECD members (38 paises, lista estavel 2024-2026).
OECD: frozenset[str] = frozenset(
    {
        "AUS",
        "AUT",
        "BEL",
        "CAN",
        "CHE",
        "CHL",
        "COL",
        "CRI",
        "CZE",
        "DEU",
        "DNK",
        "ESP",
        "EST",
        "FIN",
        "FRA",
        "GBR",
        "GRC",
        "HUN",
        "IRL",
        "ISL",
        "ISR",
        "ITA",
        "JPN",
        "KOR",
        "LTU",
        "LUX",
        "LVA",
        "MEX",
        "NLD",
        "NOR",
        "NZL",
        "POL",
        "PRT",
        "SVK",
        "SVN",
        "SWE",
        "TUR",
        "USA",
    }
)
BRA_MIN_RANK = 50
BRA_MAX_RANK = 110
TOP_OECD_MIN = 5


def sanity_check(profile: str, ranked: pd.DataFrame) -> None:
    """Roda os 4 checks; levanta `RuntimeError` em violacao dura."""
    bra = ranked[ranked.index == "BRA"]
    if bra.empty:
        raise RuntimeError(f"[{profile}] BRA ausente do ranking")
    bra_rank = int(bra["rank"].iloc[0])
    if not BRA_MIN_RANK <= bra_rank <= BRA_MAX_RANK:
        log.warning(
            "[%s] BRA na posicao %d (esperado [%d, %d])",
            profile,
            bra_rank,
            BRA_MIN_RANK,
            BRA_MAX_RANK,
        )

    top10 = ranked.head(10).index.tolist()
    n_oecd = sum(1 for c in top10 if c in OECD)
    if n_oecd < TOP_OECD_MIN:
        raise RuntimeError(
            f"[{profile}] top10 tem so {n_oecd} OECD (esperado >= {TOP_OECD_MIN}). top10={top10}"
        )

    if ranked["score"].isna().any():
        raise RuntimeError(f"[{profile}] NaN em score final")
    if not ranked["score"].between(0, 100).all():
        raise RuntimeError(f"[{profile}] score fora de [0,100]")
    log.info("[%s] OK: BRA=#%d, top10 com %d OECD", profile, bra_rank, n_oecd)
