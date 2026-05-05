"""Stack Overflow Annual Developer Survey 2024.

Fonte canonica: https://survey.stackoverflow.co/datasets/

Baixamos o ZIP publico (~17MB), abrimos `survey_results_public.csv` em memoria
e calculamos a **mediana de salario anual em USD** por (pais, nivel), onde:

  - **Pleno**:  3 ≤ YearsCodePro < 8
  - **Senior**: YearsCodePro ≥ 8

Filtros:
  - `MainBranch == "I am a developer by profession"`
  - `DevType` em uma whitelist de papeis SWE/dev (exclui aluno, gerente, exec)
  - `ConvertedCompYearly` em [5k, 1M] USD (tira nonsense + outliers extremos)
  - >= 30 respondentes validos por (pais, nivel) — abaixo disso a mediana
    nao eh confiavel

Output: 2 indicadores por pais
  - `so_salary_pleno_usd_median`
  - `so_salary_senior_usd_median`
"""

from __future__ import annotations

import io
import logging
import zipfile

import pandas as pd
import requests

from country_innovation.collectors.base import Collector

log = logging.getLogger(__name__)

URL = "https://survey.stackoverflow.co/datasets/stack-overflow-developer-survey-2024.zip"
CSV_NAME = "survey_results_public.csv"
HEADERS = {
    "User-Agent": "country-innovation/0.1 (https://github.com/rodniski/world-ranking)",
}

DEV_TYPES_WHITELIST: frozenset[str] = frozenset(
    {
        "Developer, full-stack",
        "Developer, back-end",
        "Developer, front-end",
        "Developer, mobile",
        "Developer, desktop or enterprise applications",
        "Developer, embedded applications or devices",
        "Developer, game or graphics",
        "Developer, QA or test",
        "Data engineer",
        "DevOps specialist",
        "Engineering manager",
        "Cloud infrastructure engineer",
        "Engineer, site reliability",
        "Engineer, data",
    }
)

USECOLS = ["MainBranch", "DevType", "YearsCodePro", "Country", "ConvertedCompYearly"]
MIN_COMP_USD = 5_000
MAX_COMP_USD = 1_000_000
MIN_RESP_PER_BUCKET = 30
PLENO_RANGE = (3.0, 8.0)  # [3, 8)
SENIOR_MIN = 8.0
YEAR = 2024


class StackOverflowSurvey(Collector):
    source_id = "SO-DEV-2024"

    def fetch(self) -> pd.DataFrame:
        df = self._download_and_parse()
        df = self._filter_to_devs(df)
        df = self._enrich_level_and_filter(df)
        agg = self._aggregate(df)
        return self._to_long(agg)

    @staticmethod
    def _download_and_parse() -> pd.DataFrame:
        log.info("GET %s (~17MB)", URL)
        r = requests.get(URL, headers=HEADERS, timeout=180)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf, zf.open(CSV_NAME) as f:
            df = pd.read_csv(f, usecols=USECOLS)
        log.info("SO: %d respondentes totais", len(df))
        return df

    @staticmethod
    def _filter_to_devs(df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["MainBranch"] == "I am a developer by profession"]
        df = df[df["DevType"].isin(DEV_TYPES_WHITELIST)]
        log.info("SO: %d respondentes apos filtro de DevType/MainBranch", len(df))
        return df

    @staticmethod
    def _enrich_level_and_filter(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["years"] = df["YearsCodePro"].map(_parse_years)
        df["level"] = df["years"].map(_year_to_level)
        df = df.dropna(subset=["years", "level", "ConvertedCompYearly", "Country"])
        df = df[df["ConvertedCompYearly"].between(MIN_COMP_USD, MAX_COMP_USD)]
        log.info(
            "SO: %d respondentes validos (pleno/senior + salario in [%dk, %dk])",
            len(df),
            MIN_COMP_USD // 1000,
            MAX_COMP_USD // 1000,
        )
        return df

    @staticmethod
    def _aggregate(df: pd.DataFrame) -> pd.DataFrame:
        agg = (
            df.groupby(["Country", "level"], as_index=False)
            .agg(
                median_usd=("ConvertedCompYearly", "median"),
                n=("ConvertedCompYearly", "count"),
            )
            .query("n >= @MIN_RESP_PER_BUCKET")
        )
        log.info(
            "SO: %d (pais, nivel) com >= %d respostas",
            len(agg),
            MIN_RESP_PER_BUCKET,
        )
        return agg

    def _to_long(self, agg: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(
            {
                "country": agg["Country"].astype(str),
                "value": agg["median_usd"].astype(float),
                "indicator_id": agg["level"].map(lambda lvl: f"so_salary_{lvl}_usd_median"),
                "year": YEAR,
            }
        )
        return self.normalize_iso3(out, name_col="country")[
            ["iso3", "indicator_id", "value", "year"]
        ]


def _parse_years(v: object) -> float | None:
    if v == "Less than 1 year":
        return 0.5
    if v == "More than 50 years":
        return 50.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _year_to_level(years: float | None) -> str | None:
    if years is None:
        return None
    if PLENO_RANGE[0] <= years < PLENO_RANGE[1]:
        return "pleno"
    if years >= SENIOR_MIN:
        return "senior"
    return None  # juniors (< 3 anos) ficam de fora
