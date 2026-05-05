"""Schemas canonicos do pipeline.

Um indicador = uma linha em formato long.  Toda fonte normaliza pra esse
schema antes de tocar a camada `clean/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Direction = Literal[1, -1]
Dimension = Literal["TECH", "VISA", "PPP", "MACRO"]
Profile = Literal["pleno", "senior"]


@dataclass(frozen=True)
class IndicatorMeta:
    """Metadados de um indicador.  Vivem em codigo (direction, dimension sao
    fatos da fonte) e weights ficam em `weights.yaml` (ajustaveis pelo
    usuario).
    """

    indicator_id: str  # ex: "gii_overall", "wb_gni_pcap_ppp"
    name: str  # human-readable, p.ex. "GII Overall Score"
    source_id: str  # FK pro catalogo (ex: "GII-2025")
    dimension: Dimension
    direction: Direction  # +1 = maior eh melhor; -1 = menor eh melhor
    weight_in_dim: float = 1.0  # peso default dentro da dimensao
    profile: Profile | None = None  # None = aplica a todos os perfis
    notes: str = ""


# Long-format columns: (iso3, indicator_id, value, year, source_id)
LONG_COLUMNS = ["iso3", "indicator_id", "value", "year", "source_id"]
