"""Monta o dict serializavel pra `data/final/countries.json`."""

from __future__ import annotations

from typing import Any

import pandas as pd

DIMS = ("TECH", "VISA", "PPP", "MACRO")


def build_payload(
    rankings: dict[str, pd.DataFrame],
    normalized: pd.DataFrame,
    in_scope: list[str],
    weights: dict[str, float],
) -> dict[str, Any]:
    """Dict final consumido pelo dashboard SPA (`countries.json`)."""
    indicators_used = sorted(normalized["indicator_id"].unique())
    countries = [_country_entry(iso3, rankings, normalized) for iso3 in in_scope]
    return {
        "metadata": {
            "version": "0.1",
            "n_countries": len(in_scope),
            "n_indicators": len(indicators_used),
            "indicators": indicators_used,
            "weights_default": weights,
        },
        "countries": countries,
    }


def _country_entry(
    iso3: str,
    rankings: dict[str, pd.DataFrame],
    normalized: pd.DataFrame,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "iso3": iso3,
        "name": _iso3_to_name(iso3),
        "rankings": _country_rankings(iso3, rankings),
        "indicators": _country_indicators(iso3, normalized),
    }
    return entry


def _country_rankings(iso3: str, rankings: dict[str, pd.DataFrame]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key, ranked in rankings.items():
        if iso3 not in ranked.index:
            continue
        row = ranked.loc[iso3]
        out[key] = {
            "score": round(float(row["score"]), 2),
            "rank": int(row["rank"]),
            "dimensions": {d: (None if pd.isna(row[d]) else round(float(row[d]), 2)) for d in DIMS},
            "gate": row["gate"] if isinstance(row["gate"], str) else None,
        }
    return out


def _country_indicators(iso3: str, normalized: pd.DataFrame) -> dict[str, dict[str, Any]]:
    sub = normalized[normalized["iso3"] == iso3]
    return {
        r["indicator_id"]: {
            "raw": _safe_float(r["value"]),
            "score": round(float(r["score"]), 2),
            "is_imputed": bool(r["is_imputed"]),
        }
        for _, r in sub.iterrows()
    }


def _iso3_to_name(iso3: str) -> str:
    """Mapping leve via country_converter; preserva ISO3 se nao encontrar."""
    import country_converter as coco

    name = coco.CountryConverter().convert(names=iso3, src="ISO3", to="name_short")
    return name if isinstance(name, str) and name != "not found" else iso3


def _safe_float(v: Any) -> float | None:
    try:
        f = float(v)
        return None if pd.isna(f) else round(f, 4)
    except (TypeError, ValueError):
        return None
