import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st

st.set_page_config(
    page_title="El Rata · Estalvi energètic",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS directe a la portada (sempre es carrega, sense dependre de services)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%) !important;
  font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}

.portada-hero {
  background: linear-gradient(135deg, rgba(34,197,94,0.15) 0%, rgba(15,23,42,0.95) 50%);
  border: 2px solid rgba(34,197,94,0.4);
  border-radius: 24px;
  padding: 2.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(34,197,94,0.1);
}

.portada-titol {
  font-size: 2.8rem;
  font-weight: 800;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
}

.portada-titol span {
  background: linear-gradient(90deg, #22c55e, #4ade80);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.portada-subtitol {
  color: #94a3b8;
  font-size: 1.1rem;
  line-height: 1.6;
}

.portada-badge {
  display: inline-block;
  background: rgba(34,197,94,0.2);
  color: #22c55e;
  padding: 0.3rem 0.9rem;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  border: 1px solid rgba(34,197,94,0.5);
}

.portada-seccio {
  color: #94a3b8;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 2rem 0 1rem;
}

.portada-seccio span {
  color: #22c55e;
}

.portada-card {
  background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
  border: 2px solid rgba(34,197,94,0.3);
  border-radius: 20px;
  padding: 1.8rem;
  height: 100%;
  transition: all 0.3s ease;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.portada-card:hover {
  border-color: #22c55e;
  transform: translateY(-6px);
  box-shadow: 0 20px 50px rgba(34,197,94,0.15);
  background: linear-gradient(145deg, #1e3a2f 0%, #0f172a 100%);
}

.portada-card-titol {
  font-size: 1.25rem;
  font-weight: 700;
  color: #22c55e;
  margin-bottom: 0.5rem;
}

.portada-card-desc {
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.portada-chip {
  display: inline-block;
  background: rgba(34,197,94,0.15);
  color: #86efac;
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
  font-size: 0.75rem;
  margin-right: 0.3rem;
  margin-top: 0.2rem;
  border: 1px solid rgba(34,197,94,0.3);
}
</style>
""", unsafe_allow_html=True)

# Sidebar
try:
    from services.ui import render_sidebar_nav
    render_sidebar_nav()
except ImportError:
    with st.sidebar:
        st.title("El Rata")
        st.markdown("---")
        st.markdown("[Inici](/)")
        st.markdown("[Anàlisi de factura](/Anàlisi_Factura)")
        st.markdown("[Simulador Solar](/Simulador_Solar)")
        st.markdown("[Dashboard](/Dashboard)")

# Hero
st.markdown("""
<div class="portada-hero">
  <div class="portada-badge">Estalvi energètic amb IA</div>
  <h1 class="portada-titol">El Rata <span>t'ajuda a pagar menys llum</span></h1>
  <p class="portada-subtitol">
    Puja la teva factura, entén en què estàs gastant i simula unes plaques solars
    adaptades a casa teva. Tot en minuts, sense fulls de càlcul.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="portada-seccio">On vols <span>començar</span>?</p>', unsafe_allow_html=True)

# Targetes
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="portada-card">
      <div class="portada-card-titol">Anàlisi de factura</div>
      <div class="portada-card-desc">
        Extracció automàtica de consum, potència i import per detectar
        si la teva tarifa és competitiva.
      </div>
      <span class="portada-chip">OCR</span>
      <span class="portada-chip">Detecció consums</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="portada-card">
      <div class="portada-card-titol">Simulador de plaques</div>
      <div class="portada-card-desc">
        Calcula producció, autoconsum, estalvi anual i anys de retorn
        segons el teu consum i comunitat autònoma.
      </div>
      <span class="portada-chip">ROI</span>
      <span class="portada-chip">Autoconsum</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="portada-card">
      <div class="portada-card-titol">Dashboard energètic</div>
      <div class="portada-card-desc">
        Puja el teu històric de consum i deixa que l'app faci
        prediccions i recomanacions personalitzades.
      </div>
      <span class="portada-chip">Prediccions</span>
      <span class="portada-chip">Indicadors</span>
    </div>
    """, unsafe_allow_html=True)
