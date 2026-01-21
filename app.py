import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
from utils import generar_grafica

st.set_page_config(page_title="HeatUp", layout="wide", initial_sidebar_state="collapsed")

if "mode" not in st.session_state:
    st.session_state.mode = "Básico"
if "history" not in st.session_state:
    st.session_state.history = []

css = """
<style>
.stApp .block-container > div:first-child {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 9999;
}
:root {
  --bg-dark: #0f1724;
  --panel-dark: #0b1220;
  --accent: #ff6b00;
  --muted: #9aa4b2;
  --text: #e6eef6;
}
body {
  background: var(--bg-dark);
  color: var(--text);
}
.topbar {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:12px 20px;
  background: linear-gradient(90deg, rgba(16,22,30,1), rgba(10,12,18,1));
  border-radius: 0 0 10px 10px;
  box-shadow: 0 6px 18px rgba(2,6,23,0.6);
}
.topbar .left { display:flex; flex-direction:column; }
.title { font-size:28px; font-weight:800; margin:0; color:var(--text); }
.subtitle { font-size:13px; margin:0; color:var(--muted); }
.controls { display:flex; gap:10px; align-items:center; }
.btn { padding:8px 10px; border-radius:8px; border: none; cursor: pointer; font-weight:600; background: transparent; color: var(--text); }
.card { border-radius:10px; padding:14px; margin-top:12px; background: var(--panel-dark); color: var(--text); }
.small-note { font-size:13px; margin-top:8px; color:var(--muted); }
.stTable thead th { color: var(--text) !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

with st.container():
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown('<div class="topbar"><div class="left"><div class="title">HeatUp</div><div class="subtitle">Calculadora para calentar líquidos en la cocina</div></div>', unsafe_allow_html=True)
    with c2:
        mode = st.selectbox("Modo", ["Básico", "Avanzado"], index=0 if st.session_state.mode == "Básico" else 1, key="mode_top")
        st.session_state.mode = mode
    with c3:
        st.write("")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="small-note">Selecciona el modo en la barra superior. Rellena los parámetros y pulsa "Calcular tiempo".</div>', unsafe_allow_html=True)
st.markdown("---")

liquidos = {"Agua": 100, "Leche": 90, "Sopa": 95, "Café": 75, "Chocolate": 85}
fuego_factors = {"Bajo": 1.5, "Medio": 1.0, "Alto": 0.7}

col_l, col_r = st.columns([1, 1])
with col_l:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Parámetros")
    tipo = st.selectbox("Tipo de líquido", list(liquidos.keys()))
    cantidad = st.number_input("Cantidad (ml)", min_value=50, max_value=5000, value=250, step=50)
    if st.session_state.mode == "Básico":
        intensidad = st.selectbox("Intensidad del fuego", list(fuego_factors.keys()))
        temp_inicial = 25.0
    else:
        intensidad = None
        temp_inicial = st.number_input("Temperatura inicial (°C)", min_value=-10.0, max_value=100.0, value=25.0, step=1.0)
    calcular = st.button("Calcular tiempo")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Resultados")
    results_area = st.empty()
    plot_area = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

def format_minutes_seconds(minutes_float):
    total_seconds = int(round(minutes_float * 60))
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins} minutos y {secs} segundos", f"{mins:02d}:{secs:02d}", mins, secs

if calcular:
    if cantidad <= 0:
        st.error("La cantidad debe ser mayor que 0 ml.")
    else:
        temp_obj = liquidos[tipo]
        factor = fuego_factors[intensidad] if intensidad else 1.0
        tiempo_min = max((cantidad * (temp_obj - temp_inicial)) / 8000.0 * factor, 0.01)
        time_str_readable, time_str_mmss, mins, secs = format_minutes_seconds(tiempo_min)
        record = {
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tipo": tipo,
            "Cantidad (ml)": cantidad,
            "Tiempo estimado": time_str_mmss
        }
        if st.session_state.mode == "Básico":
            record["Intensidad"] = intensidad
        else:
            record["Temperatura (°C)"] = temp_inicial
        st.session_state.history.insert(0, record)
        if len(st.session_state.history) > 200:
            st.session_state.history = st.session_state.history[:200]
        resumen_md = f"**Tipo:** {tipo}  •  **Cantidad:** {cantidad} ml  •  **Temp. inicial:** {temp_inicial} °C"
        if intensidad:
            resumen_md += f"  •  **Intensidad:** {intensidad}"
        results_area.markdown(resumen_md)
        results_area.markdown(f"**Tiempo estimado:** {time_str_readable}")
        tiempo_seg = tiempo_min * 60.0
        t = np.linspace(0, tiempo_seg, 300)
        k = -np.log(0.01) / max(tiempo_seg, 1.0)
        temp = temp_obj - (temp_obj - temp_inicial) * np.exp(-k * t)
        df_plot = pd.DataFrame({"Tiempo": t, "Temperatura": temp})
        fig = generar_grafica(df_plot, dark=True)
        ax = fig.axes[0]
        ax.set_title(f"Temperatura vs Tiempo — {tipo}", color="white")
        plot_area.pyplot(fig)
        plt.close(fig)

if st.session_state.history:
    st.markdown("---")
    st.subheader("Historial de simulaciones (últimas 10)")
    hist_df = pd.DataFrame(st.session_state.history).head(10)
    display_cols = ["Fecha", "Tipo", "Cantidad (ml)"]
    if "Intensidad" in hist_df.columns:
        display_cols.append("Intensidad")
    if "Temperatura (°C)" in hist_df.columns:
        display_cols.append("Temperatura (°C)")
    display_cols.append("Tiempo estimado")
    hist_display = hist_df[display_cols].rename(columns={
        "Fecha": "Fecha",
        "Tipo": "Tipo",
        "Cantidad (ml)": "Cantidad (ml)",
        "Intensidad": "Intensidad",
        "Temperatura (°C)": "Temperatura inicial (°C)",
        "Tiempo estimado": "Tiempo estimado (MM:SS)"
    })
    st.dataframe(hist_display, use_container_width=False, width=700, height=200)
