"""
Parser per extreure dades de factures elèctriques espanyoles.
Suporta múltiples formats i companyies (Endesa, Iberdrola, Naturgy, etc.)
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class InvoiceData:
    """Dades extretes d'una factura elèctrica."""
    consum_kwh: Optional[float] = None
    potencia_kw: Optional[float] = None
    import_total: Optional[float] = None
    periode_inici: Optional[str] = None
    periode_fi: Optional[str] = None
    raw_text: str = ""


def parse_invoice_text(text: str) -> InvoiceData:
    """
    Extreu consum, potència, import i dates del text OCR d'una factura.
    """
    result = InvoiceData(raw_text=text)
    text_lower = text.lower()
    text_clean = text.replace(",", ".").replace(" ", "")

    # --- CONSUM (kWh) ---
    # Patrons comuns: "150 kWh", "150kWh", "Consumo: 150 kWh", "Energía activa: 150"
    consum_patterns = [
        r"consumo\s*(?:activo|activa)?\s*[:\s]*(\d+(?:[.,]\d+)?)\s*k?wh",
        r"energ[ií]a\s*activa\s*[:\s]*(\d+(?:[.,]\d+)?)\s*k?wh",
        r"(\d+(?:[.,]\d+)?)\s*kwh",
        r"(\d+(?:[.,]\d+)?)\s*k\s*wh",
        r"consum\s*[:\s]*(\d+(?:[.,]\d+)?)",
    ]
    for pattern in consum_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            try:
                val = float(matches[0].replace(",", "."))
                if 1 < val < 100000:  # rang raonable kWh
                    result.consum_kwh = val
                    break
            except ValueError:
                pass

    # --- POTÈNCIA (kW) ---
    potencia_patterns = [
        r"potencia\s*contractada\s*[:\s]*(\d+(?:[.,]\d+)?)\s*kw",
        r"potencia\s*[:\s]*(\d+(?:[.,]\d+)?)\s*kw",
        r"(\d+(?:[.,]\d+)?)\s*kw\s*(?:contractada|contratada)?",
        r"(\d[,.]?\d)\s*kw",
    ]
    for pattern in potencia_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            try:
                val = float(matches[0].replace(",", "."))
                if 1.0 <= val <= 15.0:
                    result.potencia_kw = val
                    break
            except ValueError:
                pass

    # --- IMPORT TOTAL (€) ---
    import_patterns = [
        r"total\s*(?:a\s*pagar|factura)?\s*[:\s]*(\d+(?:[.,]\d+)?)\s*€?",
        r"importe\s*total\s*[:\s]*(\d+(?:[.,]\d+)?)",
        r"(\d+(?:[.,]\d+)?)\s*€\s*(?:total|final)?",
        r"total\s*[:\s]*(\d+(?:[.,]\d+)?)\s*eur",
        r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*€",
    ]
    for pattern in import_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            try:
                raw = matches[-1].replace(".", "").replace(",", ".")
                val = float(raw)
                if 1 < val < 5000:
                    result.import_total = val
                    break
            except ValueError:
                pass

    # --- PERÍODE (dates) ---
    date_patterns = [
        r"(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s*[-a]\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
        r"desde\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s*hasta\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
        r"periodo\s*[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s*[-a]\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            result.periode_inici = match.group(1)
            result.periode_fi = match.group(2)
            break

    return result
