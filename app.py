import streamlit as st
import numpy as np
import pandas as pd
import time
from utils import generar_grafica

st.set_page_config(page_title="HeatUp", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "kitchen"

if "mode" not in st.session_state:
    st.session_state.mode = "Básico"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "kitchen" else "kitchen"

def toggle_mode():
    st.session_state.mode = "Avanzado" if st.session_state.mode == "Básico" else "Básico"

dark = st.session_state.theme == "dark"

st.markdown(f"""
<style>
:root {{
    --bg-kitchen: #fff1e6;
    --bg-dark: #0f172a;
    --panel-left: #7c3aed;
    --panel-right: #fb923c;
    --top-kitchen: linear-gradient(90deg, #ffedd5, #fde68a);
    --top-dark: linear-gradient(90deg, #020617, #020617);
    --text-dark: #020617;
    --text-light: #f8fafc;
}}

.stApp {{
    background-color: {'var(--bg-dark)' if dark else 'var(--bg-kitchen)'};
}}

.topbar {{
    position: sticky;
    top: 0;
    z-index: 9999;
    background: {'var(--top-dark)' if dark else 'var(--top-kitchen)'};
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #f97316;
}}

.title {{
    font-size: 28px;
    font-weight: 900;
    color: {'var(--text-light)' if dark else 'var(--text-dark)'};
}}

.controls {{
    display: flex;
    gap: 12px;
}}

.panel {{
    border-radius: 16px;
    padding: 20px;
    color: white;
}}

.left {{
    background: #6d28d9;
}}

.right {{
    background: #f97316;
}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="topbar">
    <div class="title">HeatUp</div>
    <div class="controls">
        <button onclick="window.location.reload()">🔄</button>
    </div>
</div>
""", unsafe_allow_html=True)

cbar = st.columns([1,1,1,1,1])
with cbar[3]:
    st.button("🌙 / 🔥", on_click=toggle_theme)
with cbar[4]:
    st.button(st.session_state.mode, on_click=toggle_mode)

st.markdown("---")

liquidos = {
    "Agua": 100,
    "Leche": 90,
    "Sopa": 95,
    "Café": 75,
    "Chocolate": 85
}

fuego = {
    "Bajo": 1.5,
    "Medio": 1.0,
    "Alto": 0.7
}

col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<div class="panel left">', unsafe_allow_html=True)
    st.subheader("Parámetros de cocina")
    tipo = st.selectbox("Líquido", list(liquidos.keys()))
    cantidad = st.number_input("Cantidad (ml)", 50, 2000, 250, 50)
    intensidad = st.selectbox("Fuego", list(fuego.keys()))
    calcular = st.button("Calcular tiempo")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="panel right">', unsafe_allow_html=True)

    if calcular:
        temp_i = 25
        temp_f = liquidos[tipo]
        tiempo_min = max((cantidad * (temp_f - temp_i)) / 8000 * fuego[intensidad], 0.2)
        tiempo_seg = tiempo_min * 60

        st.metric("Tiempo estimado", f"{tiempo_min:.2f} minutos")

        t = np.linspace(0, tiempo_seg, 300)
        k = -np.log(0.01) / tiempo_seg
        temp = temp_f - (temp_f - temp_i) * np.exp(-k * t)

        df = pd.DataFrame({"Tiempo": t, "Temperatura": temp})

        slot = st.empty()
        frames = 40
        delay = 3 / frames

        for i in np.linspace(5, len(df), frames, dtype=int):
            fig = generar_grafica(df.iloc[:i], dark)
            slot.pyplot(fig)
            time.sleep(delay)

    else:
        st.info("La gráfica aparecerá aquí")

    st.markdown('</div>', unsafe_allow_html=True)
