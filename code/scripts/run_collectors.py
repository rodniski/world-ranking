"""Roda os 3 coletores base e grava em data/raw/.

Uso:
    cd code
    python scripts/run_collectors.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Permitir rodar sem `pip install -e .`
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from country_innovation.collectors.gii import GII
from country_innovation.collectors.heritage import Heritage
from country_innovation.collectors.wb_ppp import WorldBankPPP

DATA_RAW = ROOT.parent / "data" / "raw"


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log = logging.getLogger("run_collectors")

    collectors = [WorldBankPPP(raw_dir=DATA_RAW), Heritage(raw_dir=DATA_RAW),
                  GII(raw_dir=DATA_RAW)]
    failures: list[tuple[str, Exception]] = []
    summary: list[tuple[str, int, int]] = []

    for c in collectors:
        try:
            df = c.run()
            summary.append((c.source_id, len(df), df["iso3"].nunique()))
        except Exception as exc:  # noqa: BLE001
            log.error("[%s] FALHA: %s", c.source_id, exc)
            failures.append((c.source_id, exc))

    log.info("=" * 60)
    log.info("RESUMO")
    for sid, rows, countries in summary:
        log.info("  %-10s  %d linhas  %d países", sid, rows, countries)
    if failures:
        log.error("Falhas em: %s", [f[0] for f in failures])
        return 1
    log.info("OK — %d fontes coletadas em %s", len(summary), DATA_RAW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
