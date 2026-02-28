def solar_production_by_region(region):
    """
    kWh produïts per kWp instal·lat a l'any, per Comunitat Autònoma.
    Fonts: PVGIS, IDAE, mitjanes irradiació solar Espanya.
    """
    production_map = {
        "Catalunya": 1550,
        "Madrid": 1650,
        "Andalusia": 1750,
        "Comunitat Valenciana": 1700,
        "País Basc": 1300,
        "Galícia": 1400,
        "Aragó": 1650,
        "Castella i Lleó": 1600,
        "Castella-La Manxa": 1700,
        "Murcia": 1750,
        "Extremadura": 1700,
        "Astúries": 1350,
        "Cantàbria": 1350,
        "Navarra": 1550,
        "La Rioja": 1650,
        "Balears": 1650,
        "Canàries": 1850,
    }
    return production_map.get(region, 1550)


def solar_production_by_city(city):
    """Compatibilitat amb codi antic (ciutats)."""
    city_to_production = {
        "Barcelona": 1550,
        "Madrid": 1650,
        "Valencia": 1700,
        "Sevilla": 1800,
        "Bilbao": 1300,
        "Zaragoza": 1650,
        "Malaga": 1750,
    }
    return city_to_production.get(city, 1500)