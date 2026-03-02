import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from ai.prediction import predict_consumption
    from ai.advisor import generate_recommendations
except ImportError:
    def predict_consumption(df):
        import pandas as pd
        if "consum_kwh" in df.columns and len(df) > 0:
            mean_val = float(df["consum_kwh"].mean())
        else:
            mean_val = 0.0
        return pd.DataFrame(
            {
                "mes": [f"Futur_{i + 1}" for i in range(12)],
                "prediccio_kwh": [mean_val] * 12,
            }
        )

    def generate_recommendations(*args):
        return ["Puja les dades per obtenir recomanacions."]

try:
    from services.ui import inject_global_css, render_sidebar_nav
    inject_global_css()
    render_sidebar_nav()
except ImportError:
    pass

try:
    from services.reference_data import get_consum_referencia, comparar_amb_referencia
    from services.sample_csv import generate_sample_consumption_csv
except ImportError:
    def get_consum_referencia(_): return 205
    def comparar_amb_referencia(c, r): return f"Mitjana: ~205 kWh/mes", c / 205
    def generate_sample_consumption_csv(cm=None): return b"mes,consum_kwh\nGen,200\nFeb,210"

# Idioma
lang = st.session_state.get("lang", "ca")
if lang == "ca":
    title = "Dashboard energètic"
    subtitle = "Controla el teu consum al llarg del temps i descobreix on pots estalviar més."
else:
    title = "Cuadro de mando energético"
    subtitle = "Controla tu consumo a lo largo del tiempo y descubre dónde puedes ahorrar más."

st.markdown(
    f'<h1 class="app-page-title">{title}</h1>'
    f'<p class="app-page-subtitle">{subtitle}</p>',
    unsafe_allow_html=True,
)

# Pre-omplir des de l'anàlisi de factura
if "invoice_consum_anual" not in st.session_state:
    st.session_state.invoice_consum_anual = None
if "invoice_preu_kwh" not in st.session_state:
    st.session_state.invoice_preu_kwh = None
if "invoice_potencia" not in st.session_state:
    st.session_state.invoice_potencia = None
if "invoice_for_dashboard" not in st.session_state:
    st.session_state.invoice_for_dashboard = False

st.sidebar.header("Configuració")
default_preu = st.session_state.invoice_preu_kwh or 0.20
default_pot = st.session_state.invoice_potencia or 4.6
preu_kwh = st.sidebar.number_input("Preu kWh (€)", 0.0, 1.0, float(default_preu))
potencia = st.sidebar.number_input("Potència contractada (kW)", 0.0, 15.0, float(default_pot))

# Plantilla CSV descarregable
if st.session_state.invoice_for_dashboard and st.session_state.invoice_consum_anual:
    consum_mensual = st.session_state.invoice_consum_anual
    if consum_mensual > 800:
        consum_mensual = consum_mensual / 12
    csv_from_invoice = generate_sample_consumption_csv(consum_mensual)
    st.success("Has vingut des de l'anàlisi de factura. Descarrega el CSV amb el consum estimat i puja'l a sota.")
    st.download_button(
        label="Descarrega CSV amb dades de la factura",
        data=csv_from_invoice,
        file_name="consum_des_factura_elrata.csv",
        mime="text/csv",
        key="download_invoice_csv",
    )
    st.session_state.invoice_for_dashboard = False
else:
    try:
        csv_bytes = generate_sample_consumption_csv()
        st.download_button(
            label="Descarrega plantilla CSV",
            data=csv_bytes,
            file_name="consum_historic_elrata.csv",
            mime="text/csv",
            key="download_csv_template",
        )
        st.caption("Format: columnes 'mes' i 'consum_kwh'. Exemple: Gen,210")
    except Exception:
        pass

uploaded_file = st.file_uploader("Puja CSV amb consum històric", type=["csv"])

if uploaded_file:

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error al llegir el CSV: {e}. Assegura't que té columnes 'mes' i 'consum_kwh'.")
        st.stop()

    # Validació
    if "consum_kwh" not in df.columns:
        st.error("El CSV ha de tenir una columna 'consum_kwh'.")
        st.stop()
    if "mes" not in df.columns:
        df["mes"] = [f"Mes_{i+1}" for i in range(len(df))]
    # Valors raonables
    if df["consum_kwh"].min() < 0 or df["consum_kwh"].max() > 5000:
        st.warning("Alguns valors de consum semblen fora de rang (0–5000 kWh). Revisa les dades.")

    consum_total = df["consum_kwh"].sum()
    cost_total = consum_total * preu_kwh
    consum_mitja = df["consum_kwh"].mean()
    energy_score = max(0, 100 - (consum_mitja / 8) - potencia * 2)

    # Dades de referència
    try:
        from services.reference_data import CONSUM_MITJA_MENSUAL, get_consum_referencia
        region_ref = st.sidebar.selectbox("Zona (per comparar)", list(CONSUM_MITJA_MENSUAL.keys()), index=0)
        ref_kwh = get_consum_referencia(region_ref)
        vs_ref = (consum_mitja / ref_kwh * 100) if ref_kwh > 0 else 100
    except Exception:
        ref_kwh = 205
        vs_ref = (consum_mitja / ref_kwh * 100) if ref_kwh > 0 else 100
        region_ref = "Espanya"

    st.markdown(
        '<h3 class="app-section-title">Resum del teu consum</h3>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Consum total", f"{consum_total:.0f} kWh")
    col2.metric("Cost anual estimat", f"{cost_total:.2f} €")
    col3.metric("Consum mitjà mensual", f"{consum_mitja:.0f} kWh")
    col4.metric("Energy Score", f"{int(energy_score)}/100")
    delta_ref = f"{(vs_ref - 100):+.0f}%" if vs_ref != 100 else "="
    col5.metric("vs mitjana zona", f"{vs_ref:.0f}%", delta_ref, help=f"Mitjana {region_ref}: ~{ref_kwh:.0f} kWh/mes")

    st.divider()

    st.markdown(
        '<h3 class="app-section-title">Històric de consum</h3>',
        unsafe_allow_html=True,
    )

    fig = px.area(
        df,
        x="mes",
        y="consum_kwh",
        template="plotly_dark",
        color_discrete_sequence=["#22c55e"],
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown(
        '<h3 class="app-section-title">Predicció futura</h3>',
        unsafe_allow_html=True,
    )

    prediction_df = predict_consumption(df)

    fig2 = px.line(
        prediction_df,
        x="mes",
        y="prediccio_kwh",
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=["#22c55e"],
        title="Predicció de consum els pròxims 12 mesos",
        labels={"mes": "Mes", "prediccio_kwh": "Consum previst (kWh)"},
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.markdown(
        '<h3 class="app-section-title">Recomanacions IA</h3>',
        unsafe_allow_html=True,
    )

    recs = generate_recommendations(consum_mitja, potencia, preu_kwh)

    for r in recs:
        st.success(r)

else:
    st.info("Puja un fitxer CSV per començar l’anàlisi.")
