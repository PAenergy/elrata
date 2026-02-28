import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
import plotly.graph_objects as go

from services.invoice_simulator import simular_factura, comparar_tarifes, DesglosFactura
from services.electricity_companies import TARIFA_INFO, get_price_factor
from services.electricity_prices import get_live_price_by_region

try:
    from services.ui import inject_global_css, render_sidebar_nav
    inject_global_css()
    render_sidebar_nav()
except ImportError:
    pass

st.markdown(
    '<h1 class="app-page-title">Simulador de factura elèctrica</h1>'
    '<p class="app-page-subtitle">Desglossa la teva factura i compara quant pagaries amb diferents tarifes. Inspirat en el '
    '<a href="https://comparador.cnmc.gob.es/facturaluz/inicio/" target="_blank" style="color:#22c55e">Comparador CNMC</a>.</p>',
    unsafe_allow_html=True,
)

st.divider()

# Pre-omplir des de l'anàlisi de factura
if "invoice_consum_anual" not in st.session_state:
    st.session_state.invoice_consum_anual = None
if "invoice_preu_kwh" not in st.session_state:
    st.session_state.invoice_preu_kwh = None
if "invoice_potencia" not in st.session_state:
    st.session_state.invoice_potencia = None

# Inputs
st.markdown("**Dades del consum**")
col1, col2, col3 = st.columns(3)

default_consum = st.session_state.invoice_consum_anual or 250
if st.session_state.invoice_consum_anual:
    if st.session_state.invoice_consum_anual > 800:
        default_consum = int(st.session_state.invoice_consum_anual / 12)
    else:
        default_consum = int(st.session_state.invoice_consum_anual)

with col1:
    consum_kwh = st.number_input(
        "Consum (kWh)",
        min_value=50,
        max_value=5000,
        value=default_consum,
        step=25,
        help="Consum del període (ex: mensual ~250 kWh)",
    )
    if st.session_state.invoice_consum_anual:
        st.caption("Pre-omplert des de la factura")

with col2:
    default_pot = st.session_state.invoice_potencia or 4.6
    potencia_kw = st.number_input(
        "Potència contractada (kW)",
        min_value=2.3,
        max_value=15.0,
        value=float(default_pot),
        step=0.1,
        help="Potència del teu contracte",
    )

with col3:
    periodes = [
        ("1 mes", 30),
        ("2 mesos", 60),
        ("3 mesos", 90),
        ("6 mesos", 180),
        ("1 any", 365),
    ]
    periodo = st.selectbox(
        "Període",
        [p[0] for p in periodes],
        index=0,
    )
    dies = next(p[1] for p in periodes if p[0] == periodo)

st.markdown("**Zona i tarifa de referència**")
col_reg, col_tar = st.columns(2)

with col_reg:
    region = st.selectbox(
        "Comunitat Autònoma",
        [
            "Catalunya", "Madrid", "Andalusia", "Comunitat Valenciana",
            "País Basc", "Galícia", "Aragó", "Castella i Lleó", "Castella-La Manxa",
            "Murcia", "Extremadura", "Astúries", "Cantàbria", "Navarra",
            "La Rioja", "Balears", "Canàries",
        ],
    )

preu_pvpc, msg_actualitzacio = get_live_price_by_region(region)

with col_tar:
    tarifa_actual = st.selectbox(
        "La teva tarifa actual (o la que vols simular)",
        list(TARIFA_INFO.keys()),
        help="PVPC és la tarifa regulada. La resta són del mercat lliure.",
    )
    factor = get_price_factor(tarifa_actual)
    preu_kwh = preu_pvpc * factor
    st.caption(f"Preu estimat: {preu_kwh:.3f} €/kWh" + (f" — {msg_actualitzacio}" if msg_actualitzacio else ""))

st.divider()

# Simular
desglos = simular_factura(consum_kwh, potencia_kw, dies, preu_kwh)

# Desglossament
st.markdown("**Desglossament de la factura**")
st.markdown(
    "Com el [Comparador CNMC](https://comparador.cnmc.gob.es/facturaluz/inicio/), la factura es desglossa en terme d'energia, "
    "potència, peaje i impostos."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Terme energia", f"{desglos.terme_energia:.2f} €")
c2.metric("Terme potencia", f"{desglos.terme_potencia:.2f} €")
c3.metric("Impostos (IE + IVA)", f"{desglos.impost_electricitat + desglos.iva:.2f} €")
c4.metric("Total factura", f"{desglos.total:.2f} €")

# Gràfic desglossament
fig_desglos = go.Figure(
    data=[
        go.Bar(
            name="Energia",
            x=["Desglossament"],
            y=[desglos.terme_energia],
            marker_color="#22c55e",
        ),
        go.Bar(
            name="Potència",
            x=["Desglossament"],
            y=[desglos.terme_potencia],
            marker_color="#3b82f6",
        ),
        go.Bar(
            name="Alquiler comptador",
            x=["Desglossament"],
            y=[desglos.alquiler_comptador],
            marker_color="#94a3b8",
        ),
        go.Bar(
            name="Impost electricitat",
            x=["Desglossament"],
            y=[desglos.impost_electricitat],
            marker_color="#f59e0b",
        ),
        go.Bar(
            name="IVA",
            x=["Desglossament"],
            y=[desglos.iva],
            marker_color="#ef4444",
        ),
    ],
    layout=go.Layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        margin=dict(t=30, b=30),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=280,
    ),
)
st.plotly_chart(fig_desglos, use_container_width=True)

st.divider()

# Comparació de tarifes (com el CNMC)
st.markdown("**Comparació amb altres tarifes**")
st.markdown(
    "Simula quant pagaries amb cada tipus de tarifa amb el mateix consum. "
    "El [Comparador oficial de la CNMC](https://comparador.cnmc.gob.es/) ofereix més de 800 ofertes verificades."
)

factors = {nom: info["factor"] for nom, info in TARIFA_INFO.items()}
comparacions = comparar_tarifes(consum_kwh, potencia_kw, dies, preu_pvpc, factors)

# Taula comparativa
import pandas as pd
df = pd.DataFrame([
    {
        "Tarifa": c.nom_tarifa,
        "Preu €/kWh": f"{c.preu_kwh:.3f}",
        "Total factura": f"{c.desglos.total:.2f} €",
        "vs PVPC": f"+{(c.factor_vs_pvpc - 1) * 100:.0f}%" if c.factor_vs_pvpc > 1 else "Referència",
    }
    for c in comparacions
])
st.dataframe(df, use_container_width=True, hide_index=True)

# Gràfic comparatiu
fig_comp = go.Figure(
    data=[
        go.Bar(
            x=[c.nom_tarifa for c in comparacions],
            y=[c.desglos.total for c in comparacions],
            marker_color=["#22c55e" if "PVPC" in c.nom_tarifa else "#64748b" for c in comparacions],
            text=[f"{c.desglos.total:.1f} €" for c in comparacions],
            textposition="outside",
        )
    ],
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        margin=dict(t=40, b=60),
        xaxis=dict(tickangle=-25),
        yaxis=dict(title="Total (€)"),
        height=320,
    ),
)
st.plotly_chart(fig_comp, use_container_width=True)

# Estalvi potencial
millor = comparacions[0]
teva_idx = next(i for i, c in enumerate(comparacions) if c.nom_tarifa == tarifa_actual)
teva = comparacions[teva_idx]
if teva_idx > 0:
    estalvi = teva.desglos.total - millor.desglos.total
    st.info(
        f"**Estalvi potencial:** Amb {millor.nom_tarifa} estalviaries **{estalvi:.2f} €** "
        f"en aquest període ({estalvi / teva.desglos.total * 100:.0f}% menys). "
        f"En un any: ~{estalvi * (365 / dies):.0f} €."
    )
else:
    st.success("La teva tarifa actual és la més econòmica d'aquestes opcions.")

st.divider()
st.markdown(
    "**Enllaços útils:** "
    "[Comparador CNMC](https://comparador.cnmc.gob.es/) · "
    "[FacturaLuz (verificar factura)](https://facturaluz2.cnmc.es/) · "
    "[Entén la teva factura](https://comparador.cnmc.gob.es/entiendeTuFactura/inicio/)"
)
