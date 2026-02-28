"""
Genera una plantilla CSV d'exemple per al Dashboard.
"""
MONTHS = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Des"]


def generate_sample_consumption_csv(consum_mensual: float | None = None) -> bytes:
    """
    Genera un CSV d'exemple amb consum mensual.
    Si consum_mensual és None, usa valors ficticis (~220 kWh/mes).
    """
    if consum_mensual is not None and consum_mensual > 0:
        consums = [consum_mensual] * 12
    else:
        consums = [195, 210, 205, 190, 200, 230, 250, 245, 220, 210, 225, 240]
    lines = ["mes,consum_kwh"]
    for m, c in zip(MONTHS, consums):
        lines.append(f"{m},{c}")
    return "\n".join(lines).encode("utf-8")
