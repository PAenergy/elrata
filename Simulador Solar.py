import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
import plotly.graph_objects as go
from services.solar import solar_production_by_region
from services.electricity_prices import electricity_price_by_region, get_live_price_by_region
from services.ui import inject_global_css, render_sidebar_nav

inject_global_css()
render_sidebar_nav()

st.markdown(
    '<h1 class="app-page-title">Simulador de plaques solars</h1>'
    '<p class="app-page-subtitle">Calcula producció, autoconsum, estalvi anual i anys de retorn abans d\'invertir.</p>',
    unsafe_allow_html=True,
)

st.divider()

# ---------------- INPUTS ----------------
# Pre-omplir des de l'anàlisi de factura si hi ha dades
if "invoice_consum_anual" not in st.session_state:
    st.session_state.invoice_consum_anual = None
if "invoice_preu_kwh" not in st.session_state:
    st.session_state.invoice_preu_kwh = None

with st.container():
    col_region, col_roof = st.columns([1.2, 1])

    with col_region:
        region = st.selectbox(
            "Comunitat Autònoma",
            [
                "Catalunya",
                "Madrid",
                "Andalusia",
                "Comunitat Valenciana",
                "País Basc",
                "Galícia",
                "Aragó",
                "Castella i Lleó",
                "Castella-La Manxa",
                "Murcia",
                "Extremadura",
                "Astúries",
                "Cantàbria",
                "Navarra",
                "La Rioja",
                "Balears",
                "Canàries",
            ],
        )

        preu_recomanat, msg_actualitzacio = get_live_price_by_region(region)
        st.info(f"Preu de referència a {region}: **{preu_recomanat:.3f} €/kWh**" + (f" — {msg_actualitzacio}" if msg_actualitzacio else " (estimació)"))
        st.caption("Des d'octubre 2025 el mercat té preus cada 15 minuts; aquí es mostra la mitjana horària de referència PVPC.")

    with col_roof:
        mida_teulada = st.slider("Superfície disponible (m²)", 10, 200, 50)
        orientacio = st.selectbox(
            "Orientació teulada",
            ["Sud", "Sud-Est / Sud-Oest", "Est / Oest", "Nord"],
        )

st.markdown("---")

col1, col2 = st.columns(2)

default_consum = st.session_state.invoice_consum_anual or 6000
if st.session_state.invoice_consum_anual:
    default_consum = int(st.session_state.invoice_consum_anual)

with col1:
    consum_anual = st.number_input(
        "Consum anual (kWh)",
        1000,
        50000,
        default_consum,
        help="Pre-omplert des de la factura si n'has analitzat una.",
    )
    if st.session_state.invoice_consum_anual:
        st.caption("Valor detectat de la factura")

with col2:
    default_preu = st.session_state.invoice_preu_kwh or float(preu_recomanat)
    preu_kwh = st.number_input(
        "Preu electricitat (€ / kWh)",
        0.05,
        1.0,
        float(default_preu),
    )

cost_instalacio_kw = 1200

# ---------------- POTÈNCIA ----------------

kw_instalables = mida_teulada / 5

# ---------------- PRODUCCIÓ ----------------

produccio_kw = solar_production_by_region(region)
produccio_anual = kw_instalables * produccio_kw

orientation_factor = {
    "Sud": 1.0,
    "Sud-Est / Sud-Oest": 0.92,
    "Est / Oest": 0.80,
    "Nord": 0.60,
}

produccio_anual *= orientation_factor[orientacio]

# pèrdues sistema
produccio_anual *= 0.86

# ---------------- AUTOCONSUM REALISTA ----------------

ratio = produccio_anual / consum_anual

# model estadístic realista
autoconsum_ratio = max(0.3, min(0.8, 0.8 - 0.5 * (ratio - 1)))

autoconsum = produccio_anual * autoconsum_ratio
autoconsum = min(autoconsum, consum_anual)

excedent = max(produccio_anual - autoconsum, 0)

percent_autoconsum = (autoconsum / produccio_anual) * 100

# ---------------- ECONOMIA ----------------

preu_excedent = min(preu_kwh * 0.5, 0.12)

estalvi_autoconsum = autoconsum * preu_kwh
ingressos_excedent = excedent * preu_excedent

estalvi_total = estalvi_autoconsum + ingressos_excedent

cost_total = kw_instalables * cost_instalacio_kw

roi_anys = cost_total / estalvi_total if estalvi_total > 0 else 0

# ---------------- RESULTATS ----------------

st.markdown(
    '<h3 class="app-section-title">Resultats de la simulació</h3>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

col1.metric("Producció anual estimada", f"{produccio_anual:.0f} kWh")
col2.metric("Autoconsum real (%)", f"{percent_autoconsum:.1f}%")
col3.metric("Estalvi anual", f"{estalvi_total:.0f} €")

st.metric("Retorn inversió", f"{roi_anys:.1f} anys")

co2_estalvi = produccio_anual * 0.25
st.metric("CO₂ estalviat anual", f"{co2_estalvi:.0f} kg")

# ---------------- GRÀFIC ----------------

st.markdown("### Comparativa de consum vs producció")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=["Consum anual", "Producció solar"],
        y=[consum_anual, produccio_anual],
        marker_color=["#f97316", "#22c55e"],
    )
)

fig.update_layout(template="plotly_dark")

st.plotly_chart(fig, use_container_width=True)

if roi_anys < 7:
    st.success("Inversió molt interessant.")
elif roi_anys < 12:
    st.info("Inversió raonable.")
else:
    st.warning("⚠ ROI llarg. Revisa subvencions.")

st.caption("Model d'autoconsum basat en simulacions residencials europees.")