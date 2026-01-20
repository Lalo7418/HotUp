import streamlit as st
import numpy as np
import pandas as pd
import time
from utils import generar_grafica

st.set_page_config(page_title="HeatUp", layout="wide")

if "dark" not in st.session_state:
    st.session_state.dark = False

if "mode" not in st.session_state:
    st.session_state.mode = "Básico"

def toggle_theme():
    st.session_state.dark = not st.session_state.dark

def toggle_mode():
    st.session_state.mode = "Avanzado" if st.session_state.mode == "Básico" else "Básico"

theme = "dark" if st.session_state.dark else "light"

st.markdown(f"""
<style>
:root {{
    --bg-light: #fff7ed;
    --bg-dark: #0f172a;
    --card-purple: #a855f7;
    --card-orange: #fb923c;
    --text-light: #1e293b;
    --text-dark: #e5e7eb;
}}

body {{
    background-color: {'var(--bg-dark)' if theme == 'dark' else 'var(--bg-light)'};
}}

.stApp {{
    background-color: {'var(--bg-dark)' if theme == 'dark' else 'var(--bg-light)'};
    color: {'var(--text-dark)' if theme == 'dark' else 'var(--text-light)'};
}}

.topbar {{
    position: sticky;
    top: 0;
    z-index: 9999;
    background: {'#020617' if theme == 'dark' else '#fff1e6'};
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #e5e7eb;
}}

.title {{
    font-size: 28px;
    font-weight: 900;
}}

.controls {{
    display: flex;
    gap: 10px;
}}

.box-purple {{
    border: 3px solid var(--card-purple);
    border-radius: 12px;
    padding: 20px;
}}

.box-orange {{
    border: 3px solid var(--card-orange);
    border-radius: 12px;
    padding: 20px;
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

col_controls = st.columns([1,1,1,1])
with col_controls[2]:
    st.button("🌙 / ☀️", on_click=toggle_theme)
with col_controls[3]:
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

col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="box-purple">', unsafe_allow_html=True)
    tipo = st.selectbox("Tipo de líquido", list(liquidos.keys()))
    cantidad = st.number_input("Cantidad (ml)", 50, 2000, 250, 50)
    intensidad = st.selectbox("Intensidad de fuego", list(fuego.keys()))
    calcular = st.button("Calcular tiempo")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="box-orange">', unsafe_allow_html=True)

    if calcular:
        temp_inicial = 25
        temp_final = liquidos[tipo]
        tiempo_min = max((cantidad * (temp_final - temp_inicial)) / 8000 * fuego[intensidad], 0.2)
        tiempo_seg = tiempo_min * 60

        st.metric("Tiempo estimado", f"{tiempo_min:.2f} min")

        t = np.linspace(0, tiempo_seg, 300)
        k = -np.log(0.01) / tiempo_seg
        temp = temp_final - (temp_final - temp_inicial) * np.exp(-k * t)

        df = pd.DataFrame({
            "Tiempo (s)": t,
            "Temperatura (°C)": temp
        })

        placeholder = st.empty()
        frames = 40
        delay = 3 / frames
        for i in np.linspace(5, len(df), frames, dtype=int):
            fig = generar_grafica(df.iloc[:i], theme == "dark")
            placeholder.pyplot(fig)
            time.sleep(delay)

    else:
        st.info("Aquí se mostrará la gráfica de calentamiento")

    st.markdown('</div>', unsafe_allow_html=True)
