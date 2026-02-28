import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from services.solar import solar_production_by_region
from services.electricity_prices import electricity_price_by_region, get_live_price_by_region
from services.electricity_companies import TARIFA_INFO, get_price_factor, get_tarifa_description
try:
    from services.ui import inject_global_css, render_sidebar_nav
    inject_global_css()
    render_sidebar_nav()
except ImportError:
    pass

st.markdown(
    '<h1 class="app-page-title">Simulador de plaques solars</h1>'
    '<p class="app-page-subtitle">Calcula producció, autoconsum, estalvi anual i anys de retorn abans d\'invertir.</p>',
    unsafe_allow_html=True,
)

st.divider()

with st.expander("Com influeix la companyia i la tarifa en el preu?"):
    st.markdown("""
    **Sí, la companyia i el tipus de tarifa influeixen molt:**
    - **PVPC (tarifa regulada)**: Preu hora a hora segons el mercat. Sovint la més barata. Sense permanència.
    - **Mercat lliure indexat**: Similar al PVPC, amb petits marges de la comercialitzadora.
    - **Mercat lliure fix**: Preu constant. Previsibilitat, però sol ser un 10–20% més car que el PVPC.
    - **Algunes ofertes del mercat lliure**: Poden ser fins a un 35% més cares que el PVPC.

    *Font: CNMC, estudis comparatius. El preu de referència que mostrem prové del mercat (ESIOS/Red Eléctrica).*
    """)

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

        preu_pvpc, msg_actualitzacio = get_live_price_by_region(region)
        tarifa = st.selectbox(
            "Tipus de tarifa / comercialitzadora",
            list(TARIFA_INFO.keys()),
            help="La companyia i el tipus de tarifa influeixen molt en el preu. PVPC és la tarifa regulada (sovint la més barata).",
        )
        factor = get_price_factor(tarifa)
        preu_recomanat = preu_pvpc * factor
        st.info(f"Preu estimat a {region}: **{preu_recomanat:.3f} €/kWh**" + (f" — {msg_actualitzacio}" if msg_actualitzacio else " (estimació)"))
        st.caption(get_tarifa_description(tarifa))

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

col1, col2, col3, col4 = st.columns(4)

col1.metric("Producció anual estimada", f"{produccio_anual:.0f} kWh")
col2.metric("Autoconsum real", f"{percent_autoconsum:.1f}%")
col3.metric("Estalvi anual", f"{estalvi_total:.0f} €")
col4.metric("Retorn inversió", f"{roi_anys:.1f} anys")

col1b, col2b, col3b, col4b = st.columns(4)

cost_factura_actual = consum_anual * preu_kwh
percent_estalvi = (estalvi_total / cost_factura_actual * 100) if cost_factura_actual > 0 else 0
co2_estalvi = produccio_anual * 0.25

col1b.metric("Cost anual sense solar", f"{cost_factura_actual:.0f} €")
col2b.metric("Estalvi anual (%)", f"{percent_estalvi:.1f}%")
col3b.metric("CO₂ estalviat", f"{co2_estalvi:.0f} kg")
col4b.metric("Cost instal·lació", f"{cost_total:.0f} €")

# Estadístiques d'estalvi a futur
st.markdown("**Estalvi projectat**")
c1, c2, c3 = st.columns(3)
c1.metric("En 1 any", f"{estalvi_total:.0f} €")
c2.metric("En 5 anys", f"{estalvi_total * 5:.0f} €")
c3.metric("En 10 anys", f"{estalvi_total * 10:.0f} €")

st.divider()

# ---------------- ESTALVI PER MESOS ----------------

MESOS = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Des"]
# Distribució mensual solar Espanya (% anual per mes)
DIST_SOLAR = [0.04, 0.05, 0.07, 0.08, 0.10, 0.11, 0.12, 0.11, 0.09, 0.07, 0.05, 0.04]
# Consum mensual típic (més calor/aire a estiu)
DIST_CONSUM = [0.09, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.08, 0.08, 0.08, 0.09]

produccio_mensual = [produccio_anual * d for d in DIST_SOLAR]
consum_mensual = [consum_anual * d for d in DIST_CONSUM]

estalvi_mensual = []
for i in range(12):
    prod_m = produccio_mensual[i]
    autoc_m = autoconsum * DIST_SOLAR[i]
    exc_m = max(prod_m - autoc_m, 0)
    est = autoc_m * preu_kwh + exc_m * preu_excedent
    estalvi_mensual.append(est)

df_mensual = pd.DataFrame({
    "Mes": MESOS,
    "Producció (kWh)": produccio_mensual,
    "Consum (kWh)": consum_mensual,
    "Estalvi (€)": estalvi_mensual,
})

# ---------------- GRÀFIC 1: ESTALVI ELS PRÒXIMS 12 MESOS ----------------

st.markdown("### Estalvi estimat els pròxims 12 mesos")

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=df_mensual["Mes"],
    y=df_mensual["Estalvi (€)"],
    name="Estalvi (€)",
    marker_color="#22c55e",
    text=[f"{v:.0f} €" for v in estalvi_mensual],
    textposition="outside",
))
fig1.update_layout(
    template="plotly_dark",
    xaxis_title="Mes",
    yaxis_title="Estalvi (€)",
    showlegend=False,
    margin=dict(t=40, b=60),
)
st.plotly_chart(fig1, use_container_width=True)

# ---------------- GRÀFIC 2: ESTALVI ACUMULAT EN ELS PRÒXIMS ANYS ----------------

st.markdown("### Estalvi acumulat en els pròxims anys")

anys_mostrar = min(25, max(15, int(roi_anys) + 5))
anys = list(range(1, anys_mostrar + 1))
estalvi_acumulat = [estalvi_total * a for a in anys]
inversio_linea = [cost_total] * anys_mostrar

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=anys,
    y=estalvi_acumulat,
    mode="lines+markers",
    name="Estalvi acumulat",
    line=dict(color="#22c55e", width=3),
    fill="tozeroy",
))
fig2.add_trace(go.Scatter(
    x=anys,
    y=inversio_linea,
    mode="lines",
    name="Cost instal·lació",
    line=dict(color="#f97316", width=2, dash="dash"),
))
fig2.update_layout(
    template="plotly_dark",
    xaxis_title="Anys",
    yaxis_title="€",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(t=60),
)
st.plotly_chart(fig2, use_container_width=True)

st.caption("El punt que talla la línia de cost indica quan recuperes la inversió.")

# ---------------- GRÀFIC 3: PRODUCCIÓ VS CONSUM MENSUAL ----------------

st.markdown("### Producció solar vs consum mensual")

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=MESOS,
    y=produccio_mensual,
    name="Producció solar",
    marker_color="#22c55e",
))
fig3.add_trace(go.Bar(
    x=MESOS,
    y=consum_mensual,
    name="Consum",
    marker_color="#64748b",
))
fig3.update_layout(
    template="plotly_dark",
    barmode="group",
    xaxis_title="Mes",
    yaxis_title="kWh",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig3, use_container_width=True)

# ---------------- GRÀFIC 4: COMPARATIVA ANUAL ----------------

st.markdown("### Resum anual: consum vs producció")

fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=["Consum anual", "Producció solar", "Autoconsum"],
    y=[consum_anual, produccio_anual, autoconsum],
    marker_color=["#f97316", "#22c55e", "#4ade80"],
    text=[f"{consum_anual:.0f} kWh", f"{produccio_anual:.0f} kWh", f"{autoconsum:.0f} kWh"],
    textposition="outside",
))
fig4.update_layout(
    template="plotly_dark",
    xaxis_title="",
    yaxis_title="kWh",
    showlegend=False,
)
st.plotly_chart(fig4, use_container_width=True)

# ---------------- GRÀFIC 5: PIE - BALANÇ ENERGÈTIC ----------------

st.markdown("### Balanç energètic")

grid_necessari = max(consum_anual - autoconsum, 0)
labels_pie = ["Autoconsum solar", "Xarxa elèctrica", "Excedent venut"]
values_pie = [autoconsum, grid_necessari, excedent]
colors_pie = ["#22c55e", "#f97316", "#38bdf8"]

fig5 = go.Figure(data=[go.Pie(
    labels=labels_pie,
    values=values_pie,
    hole=0.4,
    marker_colors=colors_pie,
    textinfo="label+percent",
)])
fig5.update_layout(
    template="plotly_dark",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom"),
    margin=dict(t=20, b=20),
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

if roi_anys < 7:
    st.success("Inversió molt interessant.")
elif roi_anys < 12:
    st.info("Inversió raonable.")
else:
    st.warning("ROI llarg. Revisa subvencions.")

st.caption("Model d'autoconsum basat en simulacions residencials europees.")
