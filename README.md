# El Rata

Plataforma per reduir despeses: anàlisi de factures elèctriques i recomanacions de plaques solars.

---

## Com executar

1. Obre un terminal a la carpeta del projecte.

2. Instal·la les dependències:
   ```bash
   pip install -r requirements.txt
   ```

3. Executa l’aplicació:
   ```bash
   streamlit run Inici.py
   ```

4. S’obrirà el navegador amb la web. Si no, entra a: **http://localhost:8501**

---

## Preus en temps real (opcional)

Per obtenir preus PVPC actualitzats des de Red Eléctrica:

1. Sol·licita un token gratuït a `consultasios@ree.es` (tema: "Personal token request")
2. Defineix la variable d'entorn `ESIOS_API_KEY` amb el token
3. A Streamlit Cloud: Settings → Secrets → afegir `ESIOS_API_KEY`

---

## Estructura

- **Inici.py** — Pàgina principal
- **pages/Anàlisi Factura.py** — Puja una factura i extreu consum, potència i import
- **pages/Simulador Solar.py** — Simula plaques solars i ROI
- **pages/Dashboard.py** — Consum històric i prediccions
