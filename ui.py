import streamlit as st


def inject_global_css():
    """Aplica un estil fosc modern a tota l'app."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg-gradient: radial-gradient(circle at top left, #1f2937 0, #020617 45%, #000000 100%);
  --card-bg: rgba(15,23,42,0.96);
  --card-border: rgba(148,163,184,0.25);
  --accent: #22c55e;
  --accent-soft: rgba(34,197,94,0.16);
  --text-main: #e5e7eb;
  --text-muted: #9ca3af;
}

[data-testid="stAppViewContainer"] {
  background: var(--bg-gradient);
  color: var(--text-main);
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stAppViewContainer"] * {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stHeader"] {
  background: linear-gradient(to right, rgba(15,23,42,0.95), rgba(15,23,42,0.4));
  border-bottom: 1px solid rgba(148,163,184,0.2);
}

[data-testid="stSidebar"] {
  background: linear-gradient(to bottom, #020617, #020617);
  border-right: 1px solid rgba(31,41,55,0.9);
}

.block-container {
  padding-top: 2.5rem;
  padding-bottom: 3rem;
}

.app-hero {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  align-items: center;
  justify-content: space-between;
  padding: 1.8rem 2rem;
  border-radius: 1.75rem;
  background: radial-gradient(circle at top left, rgba(34,197,94,0.12), transparent 55%),
              linear-gradient(135deg, rgba(15,23,42,0.98), rgba(15,23,42,0.92));
  border: 1px solid rgba(148,163,184,0.25);
  box-shadow: 0 24px 60px rgba(15,23,42,0.95);
}

.app-hero-left {
  max-width: 520px;
}

.app-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  background: rgba(34,197,94,0.12);
  border: 1px solid rgba(34,197,94,0.55);
  font-size: 0.8rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
}

.app-hero-title {
  font-size: 3.2rem;
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: -0.04em;
  margin: 0.8rem 0 0.5rem;
}

.app-hero-title span {
  background: linear-gradient(120deg, #22c55e, #a3e635);
  -webkit-background-clip: text;
  color: transparent;
}

.app-hero-subtitle {
  font-size: 1.05rem;
  color: var(--text-muted);
  max-width: 32rem;
}

.app-hero-grid {
  display: grid;
  grid-template-columns: minmax(0,1fr);
  gap: 0.65rem;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.app-hero-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  background: rgba(15,23,42,0.9);
  border: 1px solid rgba(55,65,81,0.9);
  font-size: 0.78rem;
}

.app-section-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 1.8rem 0 1.1rem;
}

.app-section-title span {
  color: var(--accent);
}

.app-card {
  border-radius: 1.3rem;
  padding: 1.4rem 1.35rem;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  box-shadow: 0 18px 40px rgba(15,23,42,0.9);
  transition: transform 0.18s ease-out, box-shadow 0.18s ease-out, border-color 0.18s ease-out, background 0.18s ease-out;
}

.app-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 26px 60px rgba(15,23,42,1);
  border-color: rgba(34,197,94,0.6);
  background: linear-gradient(135deg, rgba(15,23,42,1), rgba(6,78,59,0.75));
}

.app-card-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.app-card-description {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.app-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.app-chip {
  font-size: 0.78rem;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,0.6);
  color: #d1d5db;
}

.app-page-title {
  font-size: 1.8rem;
  font-weight: 650;
  margin-bottom: 0.15rem;
}

.app-page-subtitle {
  font-size: 0.95rem;
  color: var(--text-muted);
  margin-bottom: 0.9rem;
}

/* Botons principals */
.stButton > button[kind="primary"],
.stButton > button {
  border-radius: 999px;
  padding: 0.4rem 1.3rem;
  border: 1px solid rgba(34,197,94,0.75);
  background: linear-gradient(135deg,#22c55e,#16a34a);
  color: #020617;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 14px 30px rgba(22,163,74,0.45);
}

.stButton > button:hover {
  filter: brightness(1.06);
  box-shadow: 0 18px 38px rgba(22,163,74,0.7);
}

/* Metrics amb fons */
div[data-testid="stMetric"] {
  padding: 0.9rem 0.9rem 0.8rem;
  border-radius: 1rem;
  background: radial-gradient(circle at top left, rgba(34,197,94,0.16), rgba(15,23,42,0.98));
  border: 1px solid rgba(55,65,81,0.95);
}

/* Inputs més foscos */
input, textarea, select {
  border-radius: 0.7rem !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )

