"""Pipeline ETL final: raw CSVs -> data/final/countries.json.

Sequencia:
    1) le todos os CSVs em data/raw/
    2) concatena em long DataFrame
    3) normaliza (direction -> coverage filter -> impute -> z-score -> 0-100)
    4) para cada perfil (pleno/senior): agrega dimensoes, aplica gates,
       score final
    5) sanity checks (BRA em [50,110], top10 com >=5 OECD, sem NaN, em [0,100])
    6) escreve countries.json no formato consumido pelo dashboard
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd
import yaml

from country_innovation.aggregator import (
    aggregate_dimension,
    apply_gates,
    final_score,
)
from country_innovation.countries import is_in_scope
from country_innovation.indicators import REGISTRY
from country_innovation.normalizers.transforms import normalize_long
from country_innovation.payload import build_payload
from country_innovation.schema import LONG_COLUMNS
from country_innovation.validation import sanity_check

log = logging.getLogger(__name__)


def build(raw_dir: Path, weights_yaml: Path, out_path: Path) -> dict:
    """Executa o pipeline e devolve o dict de countries.json (tambem salva)."""
    long_df = _load_all_csvs(raw_dir)
    in_scope = _in_scope_iso3(long_df)
    log.info("escopo = %d paises", len(in_scope))

    normalized = normalize_long(long_df, in_scope_iso3=in_scope)
    weights = _load_weights(weights_yaml)

    rankings = _compute_rankings(normalized, weights)
    payload = build_payload(rankings, normalized, in_scope, weights)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    log.info(
        "countries.json escrito em %s (%d paises)",
        out_path,
        len(payload["countries"]),
    )
    return payload


def _compute_rankings(
    normalized: pd.DataFrame, weights: dict[str, float]
) -> dict[str, pd.DataFrame]:
    """Agrega + gates + score + sanity check para os 2 perfis."""
    rankings: dict[str, pd.DataFrame] = {}
    for profile in ("pleno", "senior"):
        wide = aggregate_dimension(normalized, profile=profile)
        wide = apply_gates(wide)
        ranked = final_score(wide, weights)
        sanity_check(profile, ranked)
        rankings[f"{profile}_local"] = ranked
    return rankings


def _load_all_csvs(raw_dir: Path) -> pd.DataFrame:
    frames = [pd.read_csv(p) for p in sorted(raw_dir.glob("*.csv"))]
    if not frames:
        raise RuntimeError(f"nenhum CSV em {raw_dir}")
    df = pd.concat(frames, ignore_index=True)
    missing = set(LONG_COLUMNS) - set(df.columns)
    if missing:
        raise RuntimeError(f"colunas faltando: {missing}")
    df = df[df["indicator_id"].isin(REGISTRY.keys())]
    log.info("loaded %d linhas de %d CSVs", len(df), len(frames))
    return df


def _in_scope_iso3(df: pd.DataFrame) -> list[str]:
    """Codigos validos: 193 membros da ONU + 4 entidades especiais
    (XKX, TWN, HKG, MAC). Filtra agregados regionais tipo `AFQ`.
    """
    candidates = {c for c in df["iso3"].unique() if is_in_scope(c)}
    return sorted(candidates & _valid_sovereign_iso3())


def _valid_sovereign_iso3() -> frozenset[str]:
    """Conjunto canonico do escopo: ONU + entidades especiais.

    `country_converter.data['UNmember']` filtra os 193 estados
    soberanos reconhecidos pela ONU, descartando territorios dependentes
    e agregados regionais que aparecem em algumas fontes.
    """
    import country_converter as coco

    cc = coco.CountryConverter()
    un_members = cc.data[cc.data["UNmember"].notna()]
    iso3_un: list[str] = un_members["ISO3"].dropna().unique().tolist()
    return frozenset(iso3_un) | frozenset({"XKX", "TWN", "HKG", "MAC"})


def _load_weights(yaml_path: Path) -> dict[str, float]:
    data = yaml.safe_load(yaml_path.read_text())
    return data["dimensions"]
