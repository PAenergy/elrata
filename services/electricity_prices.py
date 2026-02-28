"""
Preus elèctrics per comunitat: prioritat a dades actualitzades (PVPC/ESIOS).
Des d'octubre 2025 el mercat té preus cada 15 minuts; la web es regula sola
amb el preu de referència del dia.
"""
from __future__ import annotations

from typing import Optional

# Fallback estàtic si no hi ha connexió o l'API falla (€/kWh, mitjana 2024-2025)
_STATIC_PRICES = {
    "Catalunya": 0.22,
    "Madrid": 0.20,
    "Andalusia": 0.21,
    "Comunitat Valenciana": 0.21,
    "País Basc": 0.23,
    "Galícia": 0.20,
    "Aragó": 0.21,
    "Castella i Lleó": 0.20,
    "Castella-La Manxa": 0.20,
    "Murcia": 0.21,
    "Extremadura": 0.21,
    "Astúries": 0.22,
    "Cantàbria": 0.22,
    "Navarra": 0.21,
    "La Rioja": 0.21,
    "Balears": 0.24,
    "Canàries": 0.18,
}


def electricity_price_by_region(region: str) -> float:
    """
    Preu de referència €/kWh per a la comunitat.
    Abans s'usaven valors fixos; ara es manté per compatibilitat
    i com a fallback. Per preus actualitzats, usar get_live_price_by_region.
    """
    return _STATIC_PRICES.get(region, 0.22)


def get_live_price_by_region(region: str) -> tuple[float, Optional[str]]:
    """
    Retorna el preu de referència actualitzat (PVPC) si és possible,
    sinó el preu estàtic. Ideal perquè la web es vagi regulant sola.

    Retorna:
        (preu_eur_kwh, missatge_actualitzacio o None)
    """
    try:
        from services.pvpc import get_pvpc_price_eur_per_kwh
        return get_pvpc_price_eur_per_kwh(region)
    except Exception:
        return electricity_price_by_region(region), None
