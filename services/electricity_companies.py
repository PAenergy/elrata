"""
Informació sobre comercialitzadores i tipus de tarifa.
La companyia i el tipus de tarifa (PVPC vs mercat lliure) influeixen molt en el preu final.

Fonts: CNMC, estudis comparatius, dades 2024-2025.
"""

# Factor sobre el preu PVPC de referència segons tipus de tarifa i companyia.
# PVPC = 1.0 (preu de referència del mercat regulat)
# Mercat lliure: pot ser més car (fix) o similar (indexat)
TARIFA_INFO = {
    "PVPC (tarifa regulada)": {
        "factor": 1.0,
        "desc": "Preu hora a hora segons mercat. Sovint la més barata. Sense permanència.",
    },
    "Mercat lliure - Tarifa indexada": {
        "factor": 1.02,
        "desc": "Preu variable segons OMIE. Similar al PVPC, pot tenir petits marges.",
    },
    "Mercat lliure - Tarifa fixa (mitjana)": {
        "factor": 1.15,
        "desc": "Preu fix. Previsibilitat, però sol ser més car que PVPC.",
    },
    "Mercat lliure - Tarifa cara": {
        "factor": 1.35,
        "desc": "Ofertes amb marges alts. Revisa la teva factura.",
    },
}


def get_price_factor(tarifa_key: str) -> float:
    """Retorna el factor a aplicar sobre el preu PVPC de referència."""
    return TARIFA_INFO.get(tarifa_key, TARIFA_INFO["PVPC (tarifa regulada)"])["factor"]


def get_tarifa_description(tarifa_key: str) -> str:
    """Retorna la descripció de la tarifa."""
    return TARIFA_INFO.get(tarifa_key, {}).get("desc", "")
