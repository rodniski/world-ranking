"""Roda todos os coletores e grava em data/raw/ + Convex.

Uso:
    cd code
    python scripts/run_collectors.py

CONVEX_URL no env => upload pra Convex; sem var => so CSV (no-op silencioso).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Permitir rodar sem `pip install -e .`
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from country_innovation.collectors.base import Collector  # noqa: E402
from country_innovation.collectors.ef_epi import EFEPIIndex  # noqa: E402
from country_innovation.collectors.gii import GII  # noqa: E402
from country_innovation.collectors.gpi import GPI  # noqa: E402
from country_innovation.collectors.hdi import HDI  # noqa: E402
from country_innovation.collectors.henley import HenleyPassport  # noqa: E402
from country_innovation.collectors.heritage import Heritage  # noqa: E402
from country_innovation.collectors.imf_weo import IMFWEO  # noqa: E402
from country_innovation.collectors.numbeo import Numbeo  # noqa: E402
from country_innovation.collectors.so_dev import StackOverflowSurvey  # noqa: E402
from country_innovation.collectors.tax_rates import TaxRatesWiki  # noqa: E402
from country_innovation.collectors.wb_ppp import WorldBankPPP  # noqa: E402
from country_innovation.collectors.wb_wgi import WorldBankWGI  # noqa: E402
from country_innovation.collectors.whr import WHR  # noqa: E402

DATA_RAW = ROOT.parent / "data" / "raw"


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log = logging.getLogger("run_collectors")

    collectors: list[Collector] = [
        WorldBankPPP(raw_dir=DATA_RAW),
        WorldBankWGI(raw_dir=DATA_RAW),
        Heritage(raw_dir=DATA_RAW),
        GII(raw_dir=DATA_RAW),
        HDI(raw_dir=DATA_RAW),
        IMFWEO(raw_dir=DATA_RAW),
        HenleyPassport(raw_dir=DATA_RAW),
        WHR(raw_dir=DATA_RAW),
        GPI(raw_dir=DATA_RAW),
        EFEPIIndex(raw_dir=DATA_RAW),
        Numbeo(raw_dir=DATA_RAW),
        TaxRatesWiki(raw_dir=DATA_RAW),
        StackOverflowSurvey(raw_dir=DATA_RAW),
    ]
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
        log.info("  %-15s  %d linhas  %d paises", sid, rows, countries)
    if failures:
        log.error("Falhas em: %s", [f[0] for f in failures])
        return 1
    log.info("OK — %d fontes coletadas em %s", len(summary), DATA_RAW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
