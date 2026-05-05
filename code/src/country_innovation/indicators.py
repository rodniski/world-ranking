"""Registry dos 23 indicadores ativos do pipeline.

Cada entrada mapeia `indicator_id` -> `IndicatorMeta` com:
  - dimensao (TECH/VISA/PPP/MACRO) — onde ele entra no agregado
  - direction (+1 maior melhor, -1 menor melhor)
  - profile (None = aplica a todos; pleno/senior so para salarios)

Pesos default ficam em `code/config/weights.yaml`. Aqui so direction +
dimensao + profile, que sao fatos da fonte.

Mapeamento da metodologia (`02_metodologia.md` §6 + decisoes):
  - GII (innovation) -> TECH
  - SO Survey salarios -> TECH (filtrado por perfil)
  - HENLEY + EF-EPI -> VISA
  - WB-PPP, IMF-GDP, NUMBEO, top tax -> PPP
  - WGI x6, IEF, HDI, WHR, GPI, IMF macro -> MACRO
"""

from __future__ import annotations

from country_innovation.schema import IndicatorMeta

REGISTRY: dict[str, IndicatorMeta] = {
    # === TECH ===
    "gii_overall": IndicatorMeta(
        "gii_overall", "Global Innovation Index 2025", "GII-2025", "TECH", +1
    ),
    "so_salary_pleno_usd_median": IndicatorMeta(
        "so_salary_pleno_usd_median",
        "Stack Overflow Survey 2024 — mediana salario USD (pleno)",
        "SO-DEV-2024",
        "TECH",
        +1,
        profile="pleno",
    ),
    "so_salary_senior_usd_median": IndicatorMeta(
        "so_salary_senior_usd_median",
        "Stack Overflow Survey 2024 — mediana salario USD (senior)",
        "SO-DEV-2024",
        "TECH",
        +1,
        profile="senior",
    ),
    # === VISA ===
    "henley_visa_free": IndicatorMeta(
        "henley_visa_free", "Henley Passport Index 2026", "HENLEY-2026", "VISA", +1
    ),
    "ef_epi_score": IndicatorMeta(
        "ef_epi_score",
        "EF English Proficiency Index 2025",
        "EF-EPI-2025",
        "VISA",
        +1,
    ),
    # === PPP ===
    "wb_gni_pcap_ppp": IndicatorMeta(
        "wb_gni_pcap_ppp", "GNI per capita PPP (WB)", "WB-PPP", "PPP", +1
    ),
    "imf_gdp_pcap_usd": IndicatorMeta(
        "imf_gdp_pcap_usd", "GDP per capita USD (IMF WEO)", "IMF-WEO-2025", "PPP", +1
    ),
    "numbeo_col_index": IndicatorMeta(
        "numbeo_col_index",
        "Cost of Living Index (Numbeo)",
        "NUMBEO",
        "PPP",
        -1,  # mais caro = pior pro residente
    ),
    "numbeo_lpp_index": IndicatorMeta(
        "numbeo_lpp_index",
        "Local Purchasing Power Index (Numbeo)",
        "NUMBEO",
        "PPP",
        +1,
    ),
    "top_marginal_income_tax": IndicatorMeta(
        "top_marginal_income_tax",
        "Top marginal individual income tax (%)",
        "TAX-RATES-WIKI",
        "PPP",
        -1,
    ),
    # === MACRO ===
    "ief_overall": IndicatorMeta(
        "ief_overall", "Index of Economic Freedom 2026", "IEF-2026", "MACRO", +1
    ),
    "hdi_overall": IndicatorMeta(
        "hdi_overall", "Human Development Index 2025", "HDI-2025", "MACRO", +1
    ),
    "whr_score": IndicatorMeta("whr_score", "World Happiness Report 2025", "WHR-2025", "MACRO", +1),
    "gpi_score": IndicatorMeta("gpi_score", "Global Peace Index 2025", "GPI-2025", "MACRO", -1),
    "wgi_va": IndicatorMeta("wgi_va", "WGI — Voice and Accountability", "WB-WGI", "MACRO", +1),
    "wgi_pv": IndicatorMeta("wgi_pv", "WGI — Political Stability", "WB-WGI", "MACRO", +1),
    "wgi_ge": IndicatorMeta("wgi_ge", "WGI — Government Effectiveness", "WB-WGI", "MACRO", +1),
    "wgi_rq": IndicatorMeta("wgi_rq", "WGI — Regulatory Quality", "WB-WGI", "MACRO", +1),
    "wgi_rl": IndicatorMeta("wgi_rl", "WGI — Rule of Law", "WB-WGI", "MACRO", +1),
    "wgi_cc": IndicatorMeta("wgi_cc", "WGI — Control of Corruption", "WB-WGI", "MACRO", +1),
    "imf_inflation": IndicatorMeta(
        "imf_inflation",
        "IMF WEO — Inflation rate (%)",
        "IMF-WEO-2025",
        "MACRO",
        -1,
    ),
    "imf_unemployment": IndicatorMeta(
        "imf_unemployment",
        "IMF WEO — Unemployment rate (%)",
        "IMF-WEO-2025",
        "MACRO",
        -1,
    ),
    "imf_govt_debt_gdp": IndicatorMeta(
        "imf_govt_debt_gdp",
        "IMF WEO — Government debt (% of GDP)",
        "IMF-WEO-2025",
        "MACRO",
        -1,
    ),
}


def for_profile(profile: str | None) -> dict[str, IndicatorMeta]:
    """Filtra o registry para um perfil especifico (pleno/senior).

    Indicadores sem perfil (`profile=None`) sempre entram.  Indicadores com
    perfil so entram quando casa.
    """
    return {iid: m for iid, m in REGISTRY.items() if m.profile is None or m.profile == profile}
