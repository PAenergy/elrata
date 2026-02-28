"""
Preus elèctrics actualitzats des de Red Eléctrica (ESIOS).
Des d'octubre 2025 el mercat és quarthorari (preus cada 15 min);
l'API PVPC retorna valors horaris que fem servir com a referència.
Font: https://api.esios.ree.es - Indicador 1001 (PVPC 2.0TD).

Per preus en temps real: sol·licita token a consultasios@ree.es
i defineix la variable d'entorn ESIOS_API_KEY.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

# Cache senzill: (region, price, updated_str) per evitar crides excessives
_CACHE: dict[str, tuple[float, str, datetime]] = {}
_CACHE_TTL_MINUTES = 60

# Geo IDs ESIOS: Península, Canàries, Balears, Ceuta, Melilla
GEO_PENINSULA = 8741
GEO_CANARIAS = 8742
GEO_BALEARS = 8743
GEO_CEUTA = 8744
GEO_MELILLA = 8745

REGION_TO_GEO: dict[str, int] = {
    "Catalunya": GEO_PENINSULA,
    "Madrid": GEO_PENINSULA,
    "Andalusia": GEO_PENINSULA,
    "Comunitat Valenciana": GEO_PENINSULA,
    "País Basc": GEO_PENINSULA,
    "Galícia": GEO_PENINSULA,
    "Aragó": GEO_PENINSULA,
    "Castella i Lleó": GEO_PENINSULA,
    "Castella-La Manxa": GEO_PENINSULA,
    "Murcia": GEO_PENINSULA,
    "Extremadura": GEO_PENINSULA,
    "Astúries": GEO_PENINSULA,
    "Cantàbria": GEO_PENINSULA,
    "Navarra": GEO_PENINSULA,
    "La Rioja": GEO_PENINSULA,
    "Balears": GEO_BALEARS,
    "Canàries": GEO_CANARIAS,
}

# Fallback €/kWh si l'API falla (mitjana 2024-2025, inclou impostos)
FALLBACK_PRICE_PENINSULA = 0.21
FALLBACK_PRICE_CANARIAS = 0.18
FALLBACK_PRICE_BALEARS = 0.24


def _fetch_esios(start: datetime, end: datetime, geo_id: int) -> Optional[list[dict]]:
    """Consulta l'API ESIOS per l'indicador 1001 (PVPC) en el rang de dates."""
    try:
        import urllib.request
        import json

        start_str = start.strftime("%Y-%m-%dT%H:%M")
        end_str = end.strftime("%Y-%m-%dT%H:%M")
        url = (
            "https://api.esios.ree.es/indicators/1001"
            f"?start_date={start_str}&end_date={end_str}"
        )
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json; application/vnd.esios-api-v1+json",
            },
        )
        token = os.environ.get("ESIOS_API_KEY") or os.environ.get("ESIOS_TOKEN")
        if token:
            req.add_header("x-api-key", token)

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return None

    indicator = data.get("indicator") or data
    values = indicator.get("values")
    if not values or not isinstance(values, list):
        return None
    return values


def _values_to_eur_per_kwh(values: list[dict], geo_id: int) -> tuple[float, int]:
    """
    Converteix valors ESIOS (€/MWh) a €/kWh i retorna preu mitjà i nombre d'interval·les.
    Els valors PVPC són del terme d'energia; per comparar amb factura residencial
    s'aplica un factor si el resultat és massa baix (impostos i conceptes afegits).
    """
    total = 0.0
    count = 0
    for v in values:
        if v.get("geo_id") != geo_id:
            continue
        val = v.get("value")
        if val is None:
            continue
        # API retorna €/MWh
        eur_per_mwh = float(val)
        eur_per_kwh = eur_per_mwh / 1000.0
        total += eur_per_kwh
        count += 1
    if count == 0:
        return 0.0, 0
    avg = total / count
    # PVPC publicat sol ser terme energia; factura final sol portar ~2x (impostos, etc.)
    if avg < 0.12:
        avg = avg * 2.2
    return round(avg, 4), count


def get_pvpc_price_eur_per_kwh(region: str) -> tuple[float, Optional[str]]:
    """
    Retorna el preu de referència PVPC (€/kWh) per a la comunitat indicada
    i, si s'ha pogut obtenir de l'API, un text amb la data d'actualització.

    El mercat elèctric espanyol té preus cada 15 minuts (96 intervals/dia);
    aquí es retorna la mitjana horària del dia en curs o de l'últim dia disponible
    perquè la web es pugui anar regulant sola.
    """
    now = datetime.now(timezone(timedelta(hours=1)))
    cache_key = region
    if cache_key in _CACHE:
        price, msg, cached_at = _CACHE[cache_key]
        if (now - cached_at).total_seconds() < _CACHE_TTL_MINUTES * 60:
            return price, msg

    geo_id = REGION_TO_GEO.get(region, GEO_PENINSULA)
    tz = timezone(timedelta(hours=1))
    # Demanem avui i ahir per si avui encara no hi ha dades
    start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = now

    values = _fetch_esios(start, end, geo_id)
    if values:
        price, n = _values_to_eur_per_kwh(values, geo_id)
        if n > 0 and price > 0:
            updated = now.strftime("%d/%m/%Y %H:%M")
            _CACHE[cache_key] = (price, f"PVPC (actualitzat {updated})", now)
            return price, f"PVPC (actualitzat {updated})"
        # Si el preu surt 0, fem fallback
    # Fallback per zona
    if geo_id == GEO_CANARIAS:
        return FALLBACK_PRICE_CANARIAS, None
    if geo_id == GEO_BALEARS:
        return FALLBACK_PRICE_BALEARS, None
    return FALLBACK_PRICE_PENINSULA, None
