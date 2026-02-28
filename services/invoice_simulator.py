"""
Simulador de factura elèctrica inspirat en el Comparador CNMC.
https://comparador.cnmc.gob.es/facturaluz/inicio/

Permet:
- Desglossar la factura (energia, potencia, peaje, impostos)
- Comparar el cost amb diferents tipus de tarifa (PVPC, indexada, fixa, cara)
- Estimar l'estalvi canviant de tarifa
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Peaje potencia: ~0.04-0.05 €/kW/dia (regulat CNMC, 2.0TD)
PEAJE_POTENCIA_EUR_KW_DIA = 0.048
# Alquiler comptador: ~0.02 €/dia
ALQUILER_COMPTADOR_EUR_DIA = 0.02
# Impost sobre electricitat: 5.11269632%
IMPOST_ELECTRICITAT = 0.0511269632
# IVA domèstic: 10%
IVA_DOMESTIC = 0.10


@dataclass
class DesglosFactura:
    """Desglossament d'una factura elèctrica."""
    terme_energia: float  # €
    terme_potencia: float  # €
    alquiler_comptador: float  # €
    base_imposable: float  # €
    impost_electricitat: float  # €
    iva: float  # €
    total: float  # €
    consum_kwh: float
    potencia_kw: float
    dies: int
    preu_kwh_efectiu: float  # €/kWh (inclou tot)


@dataclass
class ComparacioTarifa:
    """Resultat de comparar una tarifa."""
    nom_tarifa: str
    preu_kwh: float
    desglos: DesglosFactura
    factor_vs_pvpc: float


def simular_factura(
    consum_kwh: float,
    potencia_kw: float,
    dies: int,
    preu_kwh_energia: float,
) -> DesglosFactura:
    """
    Simula una factura elèctrica amb desglossament.

    Args:
        consum_kwh: Consum en kWh al període
        potencia_kw: Potència contractada en kW
        dies: Nombre de dies del període (ex: 30, 60, 365)
        preu_kwh_energia: Preu €/kWh del terme d'energia (ja inclou peaje energia)

    Returns:
        DesglosFactura amb tots els conceptes
    """
    terme_energia = consum_kwh * preu_kwh_energia
    terme_potencia = potencia_kw * dies * PEAJE_POTENCIA_EUR_KW_DIA
    alquiler = dies * ALQUILER_COMPTADOR_EUR_DIA

    base_imposable = terme_energia + terme_potencia + alquiler
    impost_elec = base_imposable * IMPOST_ELECTRICITAT
    base_amb_impost = base_imposable + impost_elec
    iva = base_amb_impost * IVA_DOMESTIC
    total = base_amb_impost + iva

    preu_efectiu = total / consum_kwh if consum_kwh > 0 else 0

    return DesglosFactura(
        terme_energia=terme_energia,
        terme_potencia=terme_potencia,
        alquiler_comptador=alquiler,
        base_imposable=base_imposable,
        impost_electricitat=impost_elec,
        iva=iva,
        total=total,
        consum_kwh=consum_kwh,
        potencia_kw=potencia_kw,
        dies=dies,
        preu_kwh_efectiu=preu_efectiu,
    )


def comparar_tarifes(
    consum_kwh: float,
    potencia_kw: float,
    dies: int,
    preu_pvpc: float,
    factors_tarifa: dict[str, float],
) -> list[ComparacioTarifa]:
    """
    Compara el cost de la factura amb diferents tipus de tarifa.

    Args:
        consum_kwh: Consum en kWh
        potencia_kw: Potència contractada
        dies: Dies del període
        preu_pvpc: Preu de referència PVPC €/kWh
        factors_tarifa: Dict {nom_tarifa: factor} (ex: {"PVPC": 1.0, "Fixa": 1.15})

    Returns:
        Llista de ComparacioTarifa ordenada per total (menor primer)
    """
    resultats = []
    for nom, factor in factors_tarifa.items():
        preu = preu_pvpc * factor
        desglos = simular_factura(consum_kwh, potencia_kw, dies, preu)
        resultats.append(ComparacioTarifa(
            nom_tarifa=nom,
            preu_kwh=preu,
            desglos=desglos,
            factor_vs_pvpc=factor,
        ))
    resultats.sort(key=lambda x: x.desglos.total)
    return resultats


def estimar_estalvi_canvi_tarifa(
    consum_anual_kwh: float,
    potencia_kw: float,
    preu_actual: float,
    preu_nova: float,
) -> tuple[float, float]:
    """
    Estima l'estalvi anual (€) i el % d'estalvi canviant de tarifa.

    Returns:
        (estalvi_eur, percentatge_estalvi)
    """
    desglos_actual = simular_factura(consum_anual_kwh, potencia_kw, 365, preu_actual)
    desglos_nova = simular_factura(consum_anual_kwh, potencia_kw, 365, preu_nova)
    estalvi = desglos_actual.total - desglos_nova.total
    percent = (estalvi / desglos_actual.total * 100) if desglos_actual.total > 0 else 0
    return estalvi, percent
