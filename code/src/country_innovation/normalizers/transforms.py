"""Pipeline de normalizacao por indicador (metodologia §5).

Ordem fixa:
    1) apply_direction  (multiplica por -1 se "menor eh melhor")
    2) impute_global_median (depois do filtro de cobertura)
    3) zscore_clip      (z-score global -> clip [-3, +3])
    4) to_0_100         (escala humana, so pra leitura)

Internamente trabalhamos sempre em z. A saida 0-100 eh o que o dashboard
mostra; o agregador combina os 0-100 ja normalizados.
"""

from __future__ import annotations

import logging

import pandas as pd

from country_innovation.indicators import REGISTRY

log = logging.getLogger(__name__)

COVERAGE_THRESHOLD = 0.70  # 70% dos paises do escopo
CLIP = 3.0


def apply_direction(df: pd.DataFrame) -> pd.DataFrame:
    """Multiplica `value` por -1 quando o indicador for direction=-1."""
    df = df.copy()
    flips = {iid: meta.direction for iid, meta in REGISTRY.items()}
    df["value"] = df.apply(lambda r: r["value"] * flips.get(r["indicator_id"], 1), axis=1)
    return df


def filter_low_coverage(df: pd.DataFrame, n_in_scope: int) -> tuple[pd.DataFrame, list[str]]:
    """Descarta indicadores com cobertura < 70% (metodologia §4)."""
    cov = df.groupby("indicator_id")["iso3"].nunique() / n_in_scope
    keep = cov[cov >= COVERAGE_THRESHOLD].index
    drop = sorted(set(cov.index) - set(keep))
    if drop:
        log.warning(
            "drop %d indicadores com cobertura < %.0f%%: %s",
            len(drop),
            COVERAGE_THRESHOLD * 100,
            drop,
        )
    return df[df["indicator_id"].isin(keep)].copy(), drop


def impute_global_median(df: pd.DataFrame, in_scope_iso3: list[str]) -> pd.DataFrame:
    """Para cada indicador, completa paises do escopo faltantes com a
    mediana global (do proprio indicador) e marca `is_imputed=True`.
    """
    out_frames: list[pd.DataFrame] = []
    df["is_imputed"] = False
    for indicator_id, sub in df.groupby("indicator_id"):
        median = sub["value"].median()
        present = set(sub["iso3"])
        missing = [c for c in in_scope_iso3 if c not in present]
        if not missing:
            out_frames.append(sub)
            continue
        meta_row = sub.iloc[0]
        imputed = pd.DataFrame(
            {
                "iso3": missing,
                "indicator_id": indicator_id,
                "value": median,
                "year": meta_row["year"],
                "source_id": meta_row["source_id"],
                "is_imputed": True,
            }
        )
        out_frames.append(pd.concat([sub, imputed], ignore_index=True))
    return pd.concat(out_frames, ignore_index=True)


def zscore_clip_to_0_100(df: pd.DataFrame) -> pd.DataFrame:
    """Z-score por indicador -> clip [-3,+3] -> escala 0-100."""
    df = df.copy()
    df["score"] = df.groupby("indicator_id")["value"].transform(_zscore_to_score)
    return df


def _zscore_to_score(values: pd.Series) -> pd.Series:
    mean = values.mean()
    std = values.std(ddof=0)
    if std == 0 or pd.isna(std):
        return pd.Series(50.0, index=values.index)
    z = (values - mean) / std
    z_clipped = z.clip(-CLIP, +CLIP)
    return ((z_clipped + CLIP) * 100.0 / (2 * CLIP)).clip(0, 100)


def normalize_long(df: pd.DataFrame, in_scope_iso3: list[str]) -> pd.DataFrame:
    """Pipeline completo: direction -> filter coverage -> impute -> zscore."""
    df = apply_direction(df)
    df, _dropped = filter_low_coverage(df, n_in_scope=len(in_scope_iso3))
    df = impute_global_median(df, in_scope_iso3)
    df = zscore_clip_to_0_100(df)
    n_total = df["iso3"].nunique() * df["indicator_id"].nunique()
    n_imputed = int(df["is_imputed"].sum())
    log.info(
        "normalize: %d (pais x indicador), %d imputados (%.1f%%)",
        n_total,
        n_imputed,
        100 * n_imputed / max(n_total, 1),
    )
    if df["score"].isna().any():
        raise RuntimeError("normalize: NaN em score apos pipeline")
    if not df["score"].between(0, 100).all():
        raise RuntimeError(
            f"normalize: score fora de [0,100]: min={df['score'].min()}, max={df['score'].max()}"
        )
    return df
