import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st

try:
    from services.ui import inject_global_css, render_sidebar_nav
    inject_global_css()
    render_sidebar_nav()
except ImportError:
    pass

lang = st.session_state.get("lang", "ca")
if lang == "ca":
    title = "Contacte"
    subtitle = "Tens dubtes o suggeriments? Contacta'ns."
else:
    title = "Contacto"
    subtitle = "¿Tienes dudas o sugerencias? Contáctanos."

st.markdown(
    f'<h1 class="app-page-title">{title}</h1>'
    f'<p class="app-page-subtitle">{subtitle}</p>',
    unsafe_allow_html=True,
)

st.divider()

st.markdown("""
**El Rata** és una eina d'estalvi energètic de codi obert.

- **Problemes tècnics**: Obre un issue al repositori del projecte (si està publicat a GitHub).
- **Suggeriments**: Envia'ns un missatge amb les teves idees.
- **Col·laborar**: El codi és obert; les contribucions són benvingudes.
""")

with st.form("contacte_form"):
    nom = st.text_input("Nom (opcional)")
    email = st.text_input("Email (opcional)")
    missatge = st.text_area("Missatge", placeholder="Escriu el teu missatge...")
    enviat = st.form_submit_button("Enviar")

if enviat:
    if missatge.strip():
        st.success("Gràcies! El missatge s'ha enviat. Et respondrem si has indicat email.")
        st.info("*Nota: En aquesta versió, el formulari no envia correus reals. Per implementar-ho, caldria configurar un servei d'email (SMTP, SendGrid, etc.).*")
    else:
        st.warning("Si us plau, escriu un missatge.")
