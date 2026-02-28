import sys
from pathlib import Path

# Assegura que la carpeta del projecte és al path (Streamlit Cloud, etc.)
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st

try:
    from services.ui import inject_global_css
except ImportError:
    def inject_global_css():
        pass  # Fallback si services.ui no es troba

st.set_page_config(
    page_title="El Rata · Estalvi energètic",
    page_icon=None,
    layout="wide",
)

inject_global_css()

# ---------------- HERO ----------------

st.markdown(
    """
<div class="app-hero">
  <div class="app-hero-left">
    <div class="app-badge">Estalvi energètic amb IA</div>
    <h1 class="app-hero-title">
      El Rata <span>t’ajuda a pagar menys llum</span>
    </h1>
    <p class="app-hero-subtitle">
      Puja la teva factura, entén en què estàs gastant i simula unes plaques solars
      adaptades a casa teva. Tot en minuts, sense fulls de càlcul.
    </p>
  </div>
  <div class="app-hero-grid">
    <div class="app-hero-pill">Lectura intel·ligent de factures</div>
    <div class="app-hero-pill">Simulador de plaques amb ROI realista</div>
    <div class="app-hero-pill">Dashboard amb històric i prediccions</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<h2 class="app-section-title">On vols <span>començar</span>?</h2>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
<div class="app-card">
  <div class="app-card-title">Anàlisi de factura</div>
  <div class="app-card-description">
    Extracció automàtica de consum, potència i import per detectar
    si la teva tarifa és competitiva.
  </div>
  <div class="app-chip-row">
    <span class="app-chip">OCR</span>
    <span class="app-chip">Detecció de consums</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("Obrir anàlisi de factura", key="btn_analisi"):
        st.switch_page("pages/Anàlisi Factura.py")

with col2:
    st.markdown(
        """
<div class="app-card">
  <div class="app-card-title">Simulador de plaques</div>
  <div class="app-card-description">
    Calcula producció, autoconsum, estalvi anual i anys de retorn
    segons el teu consum i comunitat autònoma.
  </div>
  <div class="app-chip-row">
    <span class="app-chip">ROI</span>
    <span class="app-chip">Autoconsum</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("Simular plaques solars", key="btn_solar"):
        st.switch_page("pages/Simulador Solar.py")

with col3:
    st.markdown(
        """
<div class="app-card">
  <div class="app-card-title">Dashboard energètic</div>
  <div class="app-card-description">
    Puja el teu històric de consum i deixa que l’app faci
    prediccions i recomanacions personalitzades.
  </div>
  <div class="app-chip-row">
    <span class="app-chip">Prediccions</span>
    <span class="app-chip">Indicadors clau</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("Veure dashboard", key="btn_dashboard"):
        st.switch_page("pages/Dashboard.py")
