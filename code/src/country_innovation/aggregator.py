"""Agregacao por dimensao + gates + score final (metodologia §6-7).

Pipeline (input: long DataFrame normalizado com `score` em 0-100):
    1) aggregate_dimension(profile)
       -> wide DataFrame [iso3 x dim_score(TECH/VISA/PPP/MACRO)]
    2) apply_gates
       -> aplica VISA=0 (placeholder ate Task C), MACRO<25 ×0.7, MACRO<15 ×0.4
    3) final_score
       -> media ponderada das 4 dimensoes (default 25% cada)
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from country_innovation.indicators import for_profile
from country_innovation.schema import Dimension, Profile

log = logging.getLogger(__name__)

DIMS: tuple[Dimension, ...] = ("TECH", "VISA", "PPP", "MACRO")
GATE_MACRO_SOFT = 25.0  # MACRO < 25 -> ×0.7
GATE_MACRO_HARD = 15.0  # MACRO < 15 -> ×0.4
GATE_FACTORS = {"soft": 0.7, "hard": 0.4}


def aggregate_dimension(df_long: pd.DataFrame, profile: Profile) -> pd.DataFrame:
    """Combina indicadores em dimensao (media simples por enquanto).

    Filtra o registry pelo perfil para escolher os indicadores TECH certos
    (so_salary_pleno vs so_salary_senior).  Outros perfis-invariant entram
    em ambos os perfis.
    """
    metas = for_profile(profile)
    df = df_long[df_long["indicator_id"].isin(metas.keys())].copy()
    df["dimension"] = df["indicator_id"].map(lambda i: metas[i].dimension)
    wide = df.pivot_table(
        index="iso3",
        columns="dimension",
        values="score",
        aggfunc="mean",
    ).reindex(columns=list(DIMS))
    log.info(
        "aggregate(%s): %d paises x %d dimensoes; cobertura por dim = %s",
        profile,
        len(wide),
        wide.shape[1],
        {d: int(wide[d].notna().sum()) for d in DIMS},
    )
    return wide


def apply_gates(wide: pd.DataFrame) -> pd.DataFrame:
    """Adiciona coluna `gate` ('hard'/'soft'/None) baseada em MACRO.

    NOTA: gate VISA=0 sem visto viavel exige `data/manual/dnv_catalog.csv`
    (Task C, ainda nao implementado). Aqui so MACRO.
    """
    wide = wide.copy()
    macro = wide["MACRO"]
    wide["gate"] = np.where(
        macro < GATE_MACRO_HARD,
        "hard",
        np.where(macro < GATE_MACRO_SOFT, "soft", None),
    )
    n_hard = int((wide["gate"] == "hard").sum())
    n_soft = int((wide["gate"] == "soft").sum())
    log.info("gates: %d hard (×0.4), %d soft (×0.7)", n_hard, n_soft)
    return wide


def final_score(wide: pd.DataFrame, weights: dict[Dimension, float]) -> pd.DataFrame:
    """Score final ponderado + aplicacao de gates.

    Score base = sum(weight × dim_score) / sum(weight).  Gate multiplica.
    """
    _validate_weights(weights)
    out = wide.copy()
    raw = sum(weights[d] * out[d].fillna(50.0) for d in DIMS) / sum(weights.values())
    factors = pd.Series(1.0, index=out.index)
    factors = factors.where(out["gate"] != "soft", GATE_FACTORS["soft"])
    factors = factors.where(out["gate"] != "hard", GATE_FACTORS["hard"])
    out["score"] = (raw * factors).clip(0, 100)
    out["rank"] = out["score"].rank(ascending=False, method="min").astype(int)
    return out.sort_values("rank")


def _validate_weights(weights: dict[Dimension, float]) -> None:
    missing = set(DIMS) - set(weights.keys())
    if missing:
        raise ValueError(f"weights faltando dimensao(es): {missing}")
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"weights devem somar ~1.0; somam {total:.4f}")
