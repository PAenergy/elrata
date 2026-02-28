import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np


MONTHS = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Des"]


def _next_12_month_labels(last_label: str) -> list[str]:
    """Genera els noms dels pròxims 12 mesos a partir de l'últim label."""
    if last_label in MONTHS:
        start_idx = MONTHS.index(last_label)
        return [MONTHS[(start_idx + i + 1) % 12] for i in range(12)]
    # Fallback genèric
    return [f"Futur_{i + 1}" for i in range(12)]


def predict_consumption(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prediu el consum per als pròxims 12 mesos amb una tendència lineal senzilla.

    - Usa l'ordre de les files com a seqüència temporal.
    - Ajusta un model lineal sobre l'índex de mes.
    - Genera 12 punts futurs i etiqueta els mesos de forma coherent.
    """
    if "consum_kwh" not in df.columns or len(df) == 0:
        return pd.DataFrame(
            {"mes": [f"Futur_{i + 1}" for i in range(12)], "prediccio_kwh": [0.0] * 12}
        )

    df = df.copy()
    df["mes_index"] = np.arange(len(df))

    X = df[["mes_index"]]
    y = df["consum_kwh"]

    model = LinearRegression()
    try:
        model.fit(X, y)
    except Exception:
        mean_val = float(df["consum_kwh"].mean())
        return pd.DataFrame(
            {"mes": [f"Futur_{i + 1}" for i in range(12)], "prediccio_kwh": [mean_val] * 12}
        )

    horizon = 12
    future_index = np.arange(len(df), len(df) + horizon).reshape(-1, 1)
    predictions = model.predict(future_index)

    last_label = df["mes"].iloc[-1] if "mes" in df.columns and len(df) > 0 else ""
    future_months = _next_12_month_labels(last_label)

    return pd.DataFrame({"mes": future_months, "prediccio_kwh": predictions})
