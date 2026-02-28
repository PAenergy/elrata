"""
Dades de referència per comparar el consum amb mitjanes per zona.
Fonts: IDAE, CNMC, estadístiques sector 2023-2024.
"""

# Consum mitjà mensual kWh per comunitat (habitatge residencial)
CONSUM_MITJA_MENSUAL = {
    "Catalunya": 210,
    "Madrid": 195,
    "Andalusia": 220,
    "Comunitat Valenciana": 205,
    "País Basc": 190,
    "Galícia": 185,
    "Aragó": 200,
    "Castella i Lleó": 195,
    "Castella-La Manxa": 210,
    "Murcia": 215,
    "Extremadura": 205,
    "Astúries": 195,
    "Cantàbria": 190,
    "Navarra": 185,
    "La Rioja": 195,
    "Balears": 240,
    "Canàries": 195,
}

# Mitjana estatal
CONSUM_MITJA_ESTATAL = 205


def get_consum_referencia(region: str) -> float:
    """Retorna el consum mitjà mensual de referència per a la regió."""
    return CONSUM_MITJA_MENSUAL.get(region, CONSUM_MITJA_ESTATAL)


def comparar_amb_referencia(consum_mensual: float, region: str) -> tuple[str, float]:
    """
    Compara el consum amb la mitjana de la zona.
    Returns: (missatge, percentatge vs mitjana, ex: 1.2 = 20% més)
    """
    ref = get_consum_referencia(region)
    if ref <= 0:
        return "Sense dades de referència", 1.0
    ratio = consum_mensual / ref
    return f"Mitjana {region}: ~{ref:.0f} kWh/mes", ratio
