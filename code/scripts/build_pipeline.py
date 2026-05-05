"""Orquestrador: roda o ETL completo (raw -> countries.json).

Uso:
    cd code
    python scripts/build_pipeline.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from country_innovation.build_final import build  # noqa: E402

DATA_RAW = ROOT.parent / "data" / "raw"
DATA_FINAL = ROOT.parent / "data" / "final"
WEIGHTS_YAML = ROOT / "config" / "weights.yaml"
OUT_JSON = DATA_FINAL / "countries.json"


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log = logging.getLogger("build_pipeline")

    log.info("raw=%s weights=%s out=%s", DATA_RAW, WEIGHTS_YAML, OUT_JSON)
    payload = build(raw_dir=DATA_RAW, weights_yaml=WEIGHTS_YAML, out_path=OUT_JSON)
    log.info(
        "OK: %d paises, %d indicadores em %s",
        payload["metadata"]["n_countries"],
        payload["metadata"]["n_indicators"],
        OUT_JSON,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
