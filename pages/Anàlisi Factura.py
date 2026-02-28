import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st
from pdf2image import convert_from_bytes
import easyocr
import numpy as np

from services.invoice_parser import parse_invoice_text

try:
    from services.ui import inject_global_css, render_sidebar_nav
    inject_global_css()
    render_sidebar_nav()
except ImportError:
    pass  # App corre sense estils personalitzats

st.markdown(
    '<h1 class="app-page-title">Anàlisi de factura elèctrica</h1>'
    '<p class="app-page-subtitle">Puja la teva factura en PDF i deixa que l\'IA n\'extregui el consum, la potència i l\'import total.</p>',
    unsafe_allow_html=True,
)

# Factura de prova
try:
    from services.sample_invoice import generate_sample_invoice_pdf
    pdf_bytes = generate_sample_invoice_pdf()
    if pdf_bytes:
        st.download_button(
            label="Descarrega factura de prova (PDF)",
            data=pdf_bytes,
            file_name="factura_prova_elrata.pdf",
            mime="application/pdf",
            key="download_sample",
        )
        st.caption("Descarrega aquest PDF i puja'l a sota per provar l'anàlisi.")
except ImportError:
    pass

st.divider()

uploaded_pdf = st.file_uploader("Puja factura en PDF", type=["pdf"])

if uploaded_pdf:
    st.info("Convertint PDF a imatges...")

    try:
        images = convert_from_bytes(uploaded_pdf.read())
    except Exception as e:
        st.error(f"Error al llegir el PDF: {e}")
        st.stop()

    st.info("Inicialitzant OCR (EasyOCR)...")
    reader = easyocr.Reader(["es", "ca"])

    text_total = ""

    for img in images:
        img_array = np.array(img)
        results = reader.readtext(img_array)
        for (bbox, text, prob) in results:
            text_total += text + "\n"

    # Parsejar amb el servei millorat
    data = parse_invoice_text(text_total)

    st.markdown(
        '<h3 class="app-section-title">Text extret de la factura</h3>',
        unsafe_allow_html=True,
    )
    st.text_area("Resultat OCR", text_total, height=260, key="ocr_result")

    st.divider()
    st.markdown(
        '<h3 class="app-section-title">Dades detectades</h3>',
        unsafe_allow_html=True,
    )

    # Fix bug: sempre definir consum_detectat
    consum_detectat = data.consum_kwh
    consum_display = f"{consum_detectat:.1f} kWh" if consum_detectat else "No detectat"

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Consum", consum_display)
    col2.metric(
        "Potència",
        f"{data.potencia_kw:.1f} kW" if data.potencia_kw else "—",
    )
    col3.metric(
        "Import total",
        f"{data.import_total:.2f} €" if data.import_total else "—",
    )
    col4.metric(
        "Període",
        f"{data.periode_inici or '—'} a {data.periode_fi or '—'}"
        if data.periode_inici
        else "—",
    )

    if consum_detectat or data.import_total:
        st.success("Factura analitzada correctament ✅")
    else:
        st.warning(
            "Algunes dades no s'han pogut detectar. Revisa el text OCR i introdueix-les manualment al simulador."
        )

    # Botó per anar al simulador solar amb dades pre-omplertes
    if consum_detectat:
        # Estimar consum anual: si el consum detectat sembla mensual (< 800 kWh), anualitzar
        consum_anual_estim = consum_detectat
        if consum_detectat < 800:
            consum_anual_estim = consum_detectat * 12
            st.caption(
                "El consum detectat sembla mensual. S'ha estimat el consum anual (×12) per al simulador."
            )

        # Estimar preu kWh si tenim import i consum
        preu_estim = None
        if data.import_total and consum_detectat and consum_detectat > 0:
            preu_estim = data.import_total / consum_detectat
            if preu_estim > 0.5 or preu_estim < 0.05:
                preu_estim = None  # Fora de rang raonable

        st.divider()

        if st.button("Veure recomanacions de plaques solars", type="primary"):
            st.session_state.invoice_consum_anual = consum_anual_estim
            st.session_state.invoice_preu_kwh = preu_estim
            st.switch_page("pages/Simulador Solar.py")

else:
    st.info("Puja una factura en PDF per començar l'anàlisi.")
