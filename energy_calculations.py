def energy_score(consum_anual, potencia_kw, preu_kwh):

    # valors basats en mitjana Espanya habitatge
    consum_ref = 3500
    potencia_ref = 4.6
    preu_ref = 0.20

    score = 100

    score -= (consum_anual - consum_ref) / 100
    score -= (potencia_kw - potencia_ref) * 5
    score -= (preu_kwh - preu_ref) * 120

    return max(0, min(100, int(score)))


def estimated_savings(consum_anual):
    """
    Segons estudis UE:
    optimització energètica pot reduir 10-18%
    """
    return consum_anual * 0.14