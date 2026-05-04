"""Normalização de identidade de país → ISO3 alpha-3.

Lida com casos especiais que `country_converter` não cobre bem por padrão.
"""
from __future__ import annotations

from functools import lru_cache

import country_converter as coco

# Casos especiais explícitos.  Adicionar conforme aparecerem nas fontes.
MANUAL_OVERRIDES: dict[str, str] = {
    "Kosovo": "XKX",
    "Republic of Kosovo": "XKX",
    "Taiwan": "TWN",
    "Taiwan, China": "TWN",
    "Taiwan, Province of China": "TWN",
    "Chinese Taipei": "TWN",
    "Hong Kong": "HKG",
    "Hong Kong SAR, China": "HKG",
    "Hong Kong, China": "HKG",
    "Macao": "MAC",
    "Macao, China": "MAC",
    "Macao SAR, China": "MAC",
    "Korea, Rep.": "KOR",
    "Korea, Republic of": "KOR",
    "Korea, Dem. People's Rep.": "PRK",
    "Czechia": "CZE",
    "Czech Republic": "CZE",
    "Türkiye": "TUR",
    "Turkey": "TUR",
    "United States": "USA",
    "United Kingdom": "GBR",
    "Russia": "RUS",
    "Iran": "IRN",
    "Iran, Islamic Rep.": "IRN",
    "Venezuela": "VEN",
    "Venezuela, RB": "VEN",
    "Egypt": "EGY",
    "Egypt, Arab Rep.": "EGY",
    "Slovak Republic": "SVK",
    "Yemen, Rep.": "YEM",
    "Syrian Arab Republic": "SYR",
    "Lao PDR": "LAO",
    "Lao People's Democratic Republic": "LAO",
    "Brunei Darussalam": "BRN",
    "Cabo Verde": "CPV",
    "Cape Verde": "CPV",
    "Côte d'Ivoire": "CIV",
    "Cote d'Ivoire": "CIV",
    "Curaçao": "CUW",
    "Eswatini": "SWZ",
    "St. Kitts and Nevis": "KNA",
    "St. Lucia": "LCA",
    "St. Vincent and the Grenadines": "VCT",
    "Bahamas, The": "BHS",
    "Gambia, The": "GMB",
    "Congo, Dem. Rep.": "COD",
    "Congo, Rep.": "COG",
}

_cc = coco.CountryConverter()


@lru_cache(maxsize=4096)
def to_iso3(name: str) -> str | None:
    """Converte nome de país para ISO3 alpha-3.  Retorna None se não reconhecer.

    Aplica overrides manuais antes de delegar pro country_converter pra evitar
    classificações erradas.
    """
    if not isinstance(name, str):
        return None
    name = name.strip()
    if not name:
        return None
    if name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[name]
    iso3 = _cc.convert(names=name, to="ISO3", not_found=None)
    if iso3 is None or iso3 == "not found":
        return None
    return iso3


# Whitelist do escopo: ~190 países sovereign.  Construída a partir do ISO3 oficial.
# Usar `is_in_scope(iso3)` antes de juntar com o ranking — exclui dependências e
# entidades sem cobertura suficiente nos índices.
SCOPE_BLACKLIST: frozenset[str] = frozenset({
    # Territórios/dependências sem cobertura suficiente nos índices compostos
    "ATA", "BVT", "IOT", "CXR", "CCK", "COK", "FLK", "GUF", "PYF", "ATF",
    "GIB", "GLP", "GUM", "HMD", "VAT", "MTQ", "MYT", "MNP", "NCL", "NIU",
    "NFK", "PCN", "REU", "BLM", "SHN", "MAF", "SPM", "SGS", "TKL", "UMI",
    "VIR", "WLF", "ESH",
})


def is_in_scope(iso3: str) -> bool:
    """True se o ISO3 deve entrar no ranking global."""
    return isinstance(iso3, str) and len(iso3) == 3 and iso3 not in SCOPE_BLACKLIST
