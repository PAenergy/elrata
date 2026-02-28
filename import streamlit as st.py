import streamlit as st
import plotly.express as px
import pandas as pd

# CONFIGURACIÓ PÀGINA
st.set_page_config(
    page_title="EnergyBrain",
    page_icon="⚡",
    layout="wide"
)

# ESTILS PERSONALITZATS
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #00E5FF;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# HEADER
st.title("⚡ EnergyBrain")
st.markdown("### Optimitza la teva factura elèctrica amb intel·ligència")

st.divider()

# SECCIÓ 1 — DADES BÀSIQUES
st.header("📊 Anàlisi del teu consum")

col1, col2 = st.columns(2)

with col1:
    consum = st.number_input("Consum mensual (kWh)", min_value=0.0, value=300.0)
with col2:
    preu = st.number_input("Preu per kWh (€)", min_value=0.0, value=0.20)

if st.button("Calcula Cost"):
    cost_mensual = consum * preu
    cost_anual = cost_mensual * 12

    col1, col2 = st.columns(2)
    col1.metric("Cost mensual estimat", f"{cost_mensual:.2f} €")
    col2.metric("Cost anual estimat", f"{cost_anual:.2f} €")

st.divider()

# SECCIÓ 2 — SIMULACIÓ ANUAL
st.header("📈 Simulació de Consum Anual")

mesos = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Des"]

variacio = st.slider("Variació estacional (%)", 0, 50, 10)

consum_mensual = [
    consum * (1 + (variacio/100)) if mes in ["Gen", "Feb", "Des"]
    else consum * (1 - (variacio/100)) if mes in ["Jun", "Jul", "Ago"]
    else consum
    for mes in mesos
]

df = pd.DataFrame({
    "Mes": mesos,
    "Consum (kWh)": consum_mensual
})

fig = px.line(
    df,
    x="Mes",
    y="Consum (kWh)",
    markers=True,
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# SECCIÓ 3 — SIMULADOR POTÈNCIA
st.header("⚙️ Simulador de Potència Contractada")

col1, col2 = st.columns(2)

with col1:
    potencia_actual = st.number_input("Potència actual (kW)", min_value=0.0, value=4.6)
with col2:
    nova_potencia = st.number_input("Nova potència proposada (kW)", min_value=0.0, value=3.45)

if st.button("Simular Estalvi"):
    estalvi = (potencia_actual - nova_potencia) * 40
    st.metric("Estalvi anual estimat", f"{estalvi:.2f} €")

    if estalvi > 0:
        st.success("🔋 Bona decisió! Pots reduir la teva factura.")
    else:
        st.warning("⚠️ La nova potència no genera estalvi.")