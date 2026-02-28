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

st.markdown(
    '<h1 class="app-page-title">Com funciona El Rata</h1>'
    '<p class="app-page-subtitle">Respostes a les preguntes més freqüents.</p>',
    unsafe_allow_html=True,
)

st.divider()

st.markdown("### Flux general")
st.markdown("""
1. **Anàlisi de factura**: Puja el PDF de la teva factura. L'OCR extreu consum, potència i import.
2. **Simulador de factura**: Després de l'anàlisi (o manualment), compara quant pagaries amb PVPC, tarifa indexada o fixa.
3. **Simulador Solar**: Introdueix consum anual i zona per estimar producció, autoconsum i anys de retorn.
4. **Dashboard**: Puja un CSV amb consum mensual per veure històric, prediccions i recomanacions.
""")

st.markdown("### Format del CSV al Dashboard")
st.markdown("""
El CSV ha de tenir dues columnes:
- **mes**: Nom del mes (Gen, Feb, Mar, etc.) o Mes_1, Mes_2...
- **consum_kwh**: Consum en kWh

Exemple:
```
mes,consum_kwh
Gen,210
Feb,195
Mar,220
```
Descarrega la plantilla des del Dashboard per començar.
""")

st.markdown("### D'on surten els preus?")
st.markdown("""
- **PVPC**: Preu de referència del mercat regulat (API Red Eléctrica/ESIOS). Si no hi ha token, s'usen valors mitjans 2024-2025.
- **Altres tarifes**: Factors estimats sobre el PVPC segons estudis de la CNMC i comparadors.
""")

st.markdown("### És segur pujar la meva factura?")
st.markdown("""
Sí. El processament es fa al teu navegador i al servidor de l'app. No guardem factures ni dades personals. 
Les dades extretes (consum, potència) es poden enviar als simuladors via la sessió, però no es desen de forma permanent.
""")

st.markdown("### On puc comparar totes les ofertes?")
st.markdown("""
El [Comparador oficial de la CNMC](https://comparador.cnmc.gob.es/) té més de 800 ofertes verificades. 
El nostre Simulador de factura et dóna una estimació ràpida; per ofertes concretes, consulta la CNMC.
""")

st.markdown("### Bono social")
st.markdown("""
Si tens consum i potència baixos i compleixes requisits d'ingressos, pots optar al bono social. 
Consulta els [requisits a la CNMC](https://www.cnmc.es/bono-social-electricidad).
""")
