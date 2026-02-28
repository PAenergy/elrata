import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
import pandas as pd
import plotly.express as px
from ai.prediction import predict_consumption
from ai.advisor import generate_recommendations
try:
    from services.ui import inject_global_css, render_sidebar_nav
    inject_global_css()
    render_sidebar_nav()
except ImportError:
    pass

st.markdown(
    '<h1 class="app-page-title">Dashboard energètic</h1>'
    '<p class="app-page-subtitle">Controla el teu consum al llarg del temps i descobreix on pots estalviar més.</p>',
    unsafe_allow_html=True,
)

st.sidebar.header("Configuració")
preu_kwh = st.sidebar.number_input("Preu kWh (€)", 0.0, 1.0, 0.20)
potencia = st.sidebar.number_input("Potència contractada (kW)", 0.0, 15.0, 4.6)

uploaded_file = st.file_uploader("Puja CSV amb consum històric", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    consum_total = df["consum_kwh"].sum()
    cost_total = consum_total * preu_kwh
    consum_mitja = df["consum_kwh"].mean()
    energy_score = max(0, 100 - (consum_mitja / 8) - potencia * 2)

    st.markdown(
        '<h3 class="app-section-title">Resum del teu consum</h3>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Consum total", f"{consum_total:.0f} kWh")
    col2.metric("Cost anual estimat", f"{cost_total:.2f} €")
    col3.metric("Consum mitjà mensual", f"{consum_mitja:.0f} kWh")
    col4.metric("Energy Score ⚡", f"{int(energy_score)}/100")

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
