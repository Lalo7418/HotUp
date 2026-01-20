import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from utils import cargar_csv, generar_grafica

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

def toggle_theme():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]

theme_dark = st.session_state["dark_mode"]

if theme_dark:
    page_css = """
    <style>
    :root{
        --bg:#0f1724;
        --card:#0b1220;
        --accent:#ff6b6b;
        --accent-2:#4cc9f0;
        --muted:#9aa4b2;
    }
    body {background: var(--bg); color: #e6eef6;}
    .stApp .block-container{padding-top:1.5rem; padding-left:2rem; padding-right:2rem;}
    .title {font-size:56px; font-weight:800; color: #ffffff; text-align:center; margin:0;}
    .subtitle {color: #cbd7e8; text-align:center; margin-top:8px; margin-bottom:16px;}
    .card {background: var(--card); border-radius:12px; padding:14px; box-shadow: 0 6px 18px rgba(2,6,23,0.6);}
    .input-summary {background: rgba(255,255,255,0.02); padding:10px; border-radius:8px; color:#e6eef6;}
    .small-note {color:#9aa4b2; font-size:13px; text-align:center; margin-bottom:10px;}
    </style>
    """
else:
    page_css = """
    <style>
    :root{
        --bg:#fff7ed;
        --card:#fff1e6;
        --accent:#ff6b00;
        --accent-2:#2bbf7f;
        --muted:#6b6b6b;
        --lemon:#ffd60a;
    }
    body {background: var(--bg); color: #0e1b2b;}
    .stApp .block-container{padding-top:1.5rem; padding-left:2rem; padding-right:2rem;}
    .title {font-size:56px; font-weight:800; color: #0e1b2b; text-align:center; margin:0;}
    .subtitle {color: #40515a; text-align:center; margin-top:8px; margin-bottom:16px;}
    .card {background: var(--card); border-radius:12px; padding:14px; box-shadow: 0 6px 18px rgba(0,0,0,0.04);}
    .input-summary {background: rgba(0,0,0,0.02); padding:10px; border-radius:8px; color:#0e1b2b;}
    .small-note {color:#54606a; font-size:13px; text-align:center; margin-bottom:10px;}
    </style>
    """

st.markdown(page_css, unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_mid:
    st.markdown('<p class="title">HeatUp</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Calculadora para calentar líquidos en la cocina</p>', unsafe_allow_html=True)

with col_right:
    st.button("Alternar Modo Oscuro/Claro", key="toggle-theme", on_click=toggle_theme)

st.markdown('<div class="small-note">Cambia entre "Básico" y "Avanzado" en los parámetros. Presiona "Calcular Tiempo" para actualizar resultados y animación.</div>', unsafe_allow_html=True)

modo = st.selectbox("Modo", ["Básico", "Avanzado"], index=0)

liquidos = {
    "Agua": {"temp_obj": 100},
    "Leche": {"temp_obj": 90},
    "Caldo / Sopa": {"temp_obj": 95},
    "Café (recalentar)": {"temp_obj": 75},
    "Chocolate caliente": {"temp_obj": 85}
}

fuego_factor = {
    "Bajo": 1.6,
    "Medio": 1.0,
    "Alto": 0.7
}

with st.form("calculo_form", clear_on_submit=False):
    cols = st.columns([1, 1, 1])
    with cols[0]:
        tipo = st.selectbox("Tipo de líquido", list(liquidos.keys()))
        volumen = st.number_input("Cantidad (ml)", min_value=1, value=250, step=50, format="%d")
    with cols[1]:
        if modo == "Básico":
            fuego = st.selectbox("Intensidad del fuego", ["Bajo", "Medio", "Alto"])
            temp_inicial = 25.0
        else:
            fuego = None
            temp_inicial = st.number_input("Temperatura inicial (°C)", min_value=-10.0, value=25.0, step=1.0)
    with cols[2]:
        submitted = st.form_submit_button("Calcular Tiempo")

if submitted:
    if volumen <= 0:
        st.error("La cantidad debe ser mayor que 0 ml.")
    else:
        temp_obj = liquidos[tipo]["temp_obj"]
        tiempo_base = (volumen * (temp_obj - temp_inicial)) / 8000.0
        factor = fuego_factor.get(fuego, 1.0)
        if modo == "Avanzado":
            factor = 1.0
        tiempo_real = max(tiempo_base * factor, 0.01)
        minutos = int(tiempo_real)
        segundos = int(round((tiempo_real - minutos) * 60))

        resumen_html = f"""
        <div class="input-summary">
        <strong>Tipo de líquido:</strong> {tipo} &nbsp;&nbsp;
        <strong>Cantidad:</strong> {volumen} ml &nbsp;&nbsp;
        <strong>Temperatura inicial:</strong> {temp_inicial} °C &nbsp;&nbsp;
        """
        if modo == "Básico":
            resumen_html += f"<strong>Intensidad del fuego:</strong> {fuego} &nbsp;&nbsp;"
        resumen_html += "</div>"

        st.markdown(resumen_html, unsafe_allow_html=True)
        st.metric("Tiempo estimado", f"{tiempo_real:.2f} min", delta=f"{minutos}m {segundos}s")

        total_seg = max(tiempo_real * 60.0, 1.0)
        t = np.linspace(0, total_seg, 300)
        k = -np.log(0.01) / total_seg
        temp = temp_obj - (temp_obj - temp_inicial) * np.exp(-k * t)

        if theme_dark:
            color_line = "#ff6b6b"
            color_goal = "#4cc9f0"
            text_color = "white"
            grid_alpha = 0.15
        else:
            color_line = "#ff6b00"
            color_goal = "#2bbf7f"
            text_color = "#0e1b2b"
            grid_alpha = 0.12

        frames = 45
        indices = np.linspace(5, t.size, frames, dtype=int)

        placeholder = st.empty()
        for idx in indices:
            tt = t[:idx]
            tp = temp[:idx]
            fig, ax = plt.subplots(figsize=(6.0, 3.0), tight_layout=True)
            fig.patch.set_facecolor("white" if not theme_dark else "#0b1220")
            ax.set_facecolor("white" if not theme_dark else "#0b1220")
            ax.plot(tt, tp, color=color_line, linewidth=2, label=f"Temperatura ({tipo})")
            ax.axhline(temp_obj, color=color_goal, linestyle="--", linewidth=1.25, label=f"Objetivo {temp_obj} °C")
            ax.set_title(f"Temperatura vs Tiempo — {tipo}", color=text_color, fontsize=12)
            ax.set_xlabel("Tiempo (segundos)", color=text_color, fontsize=10)
            ax.set_ylabel("Temperatura (°C)", color=text_color, fontsize=10)
            ax.tick_params(colors=text_color)
            ax.grid(alpha=grid_alpha)
            ax.legend(fontsize=9)
            placeholder.pyplot(fig)
            plt.close(fig)
            time.sleep(0.006)

        try:
            df = cargar_csv("example_data.csv")
            st.markdown("Historial")
            fig_hist = generar_grafica(df, figsize=(5.8, 2.2), theme_dark=theme_dark)
            st.pyplot(fig_hist)
            plt.close(fig_hist)
            st.dataframe(df, height=200)
        except Exception:
            pass
