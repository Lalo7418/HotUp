import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
from datetime import datetime
from utils import generar_grafica

st.set_page_config(page_title="HeatUp", layout="wide", initial_sidebar_state="collapsed")

if "theme" not in st.session_state:
    st.session_state.theme = "kitchen"  # "kitchen" = color vivo, "dark" = oscuro
if "mode" not in st.session_state:
    st.session_state.mode = "Básico"    # "Básico" or "Avanzado"
if "history" not in st.session_state:
    st.session_state.history = []

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "kitchen" else "kitchen"

def add_history(record):
    st.session_state.history.insert(0, record)
    if len(st.session_state.history) > 200:
        st.session_state.history = st.session_state.history[:200]

dark = st.session_state.theme == "dark"

css = f"""
<style>
/* Sticky topbar */
.stApp .block-container > div:first-child {{
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 9999;
}}

/* Theme variables */
:root {{
  --cook-cream: #fff7ed;
  --cook-sauce: #ff6b00;
  --cook-basil: #2bbf7f;
  --cook-lemon: #ffd60a;
  --dark-bg: #0f1724;
  --dark-panel: #0b1220;
  --dark-top: linear-gradient(90deg, rgba(16,22,30,1), rgba(10,12,18,1));
  --light-top: linear-gradient(90deg, #fff4e6, #fff9f0);
}}

body {{
  background: {'#0f1724' if dark else '#fff7ed'};
  color: {'#e6eef6' if dark else '#0e1b2b'};
}}

.topbar {{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:12px 20px;
  border-radius:0 0 10px 10px;
  background: {'var(--dark-top)' if dark else 'var(--light-top)'};
  box-shadow: {'none' if dark else '0 6px 18px rgba(0,0,0,0.04)'};
}}

.topbar .left {{
  display:flex;
  flex-direction:column;
}}

.title {{
  font-size:28px;
  font-weight:800;
  margin:0;
  color: {'#ffffff' if dark else '#0e1b2b'};
}}

.subtitle {{
  font-size:13px;
  margin:0;
  opacity:0.9;
  color: {'#cbd7e8' if dark else '#40515a'};
}}

.controls {{ display:flex; gap:8px; align-items:center; }}

.btn {{
  padding:8px 12px;
  border-radius:8px;
  border: none;
  cursor: pointer;
  font-weight:600;
}}

.btn-theme {{
  background: {'#1f2937' if dark else '#ffdcb3'};
  color: {'#e6eef6' if dark else '#0e1b2b'};
}}

.card {{
  border-radius:10px;
  padding:14px;
  margin-top:12px;
  background: {'#0b1220' if dark else '#fff6ea'};
  color: {'#e6eef6' if dark else '#0e1b2b'};
  box-shadow: {'none' if dark else '0 6px 18px rgba(0,0,0,0.03)'};
}}

.small-note {{
  font-size:13px;
  margin-top:8px;
  color: {'#9aa4b2' if dark else '#54606a'};
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

with st.container():
    cols = st.columns([1, 1, 1])
    with cols[0]:
        st.markdown(f'<div class="topbar"><div class="left"><div class="title">HeatUp</div><div class="subtitle">Calculadora para calentar líquidos en la cocina</div></div>', unsafe_allow_html=True)
    with cols[1]:
        mode = st.selectbox("Modo", ["Básico", "Avanzado"], index=0 if st.session_state.mode == "Básico" else 1, key="mode_top")
        st.session_state.mode = mode
    with cols[2]:
        theme_label = "🍳 Color" if st.session_state.theme == "kitchen" else "🌙 Oscuro"
        if st.button(theme_label, key="theme_btn", on_click=toggle_theme):
            pass
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="small-note">Selecciona el modo arriba. Rellena los parámetros y pulsa "Calcular Tiempo".</div>', unsafe_allow_html=True)
st.markdown("---")

liquidos = {"Agua":100, "Leche":90, "Sopa":95, "Café":75, "Chocolate":85}
fuego = {"Bajo":1.5, "Medio":1.0, "Alto":0.7}

col_l, col_r = st.columns([1, 1])
with col_l:
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.subheader("Parámetros")
    tipo = st.selectbox("Líquido", list(liquidos.keys()))
    cantidad = st.number_input("Cantidad (ml)", 50, 2000, 250, 50)
    if st.session_state.mode == "Básico":
        intensidad = st.selectbox("Fuego", list(fuego.keys()))
        temp_inicial = 25.0
    else:
        intensidad = None
        temp_inicial = st.number_input("Temperatura inicial (°C)", -10.0, 100.0, 25.0, 1.0)
    calcular = st.button("Calcular tiempo")
    st.markdown("</div>", unsafe_allow_html=True)

with col_r:
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.subheader("Resultados")
    placeholder_results = st.empty()
    placeholder_plot = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

if calcular:
    if cantidad <= 0:
        st.error("La cantidad debe ser mayor que 0 ml.")
    else:
        temp_f = liquidos[tipo]
        tiempo_min = max((cantidad * (temp_f - temp_inicial)) / 8000 * (fuego[intensidad] if intensidad else 1.0), 0.01)
        tiempo_seg = tiempo_min * 60

        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "tipo": tipo,
            "cantidad_ml": cantidad,
            "temp_inicial_C": temp_inicial,
            "intensidad": intensidad if intensidad else "",
            "tiempo_min": round(tiempo_min, 3)
        }
        add_history(record)

        resumen = f"**Tipo:** {tipo}   •   **Cantidad:** {cantidad} ml   •   **Temp. inicial:** {temp_inicial} °C"
        if intensidad:
            resumen += f"   •   **Intensidad:** {intensidad}"
        placeholder_results.markdown(resumen)
        st.metric("Tiempo estimado", f"{tiempo_min:.2f} min")

        t = np.linspace(0, tiempo_seg, 300)
        k = -np.log(0.01) / max(tiempo_seg, 1.0)
        temp = temp_f - (temp_f - temp_inicial) * np.exp(-k * t)
        df = pd.DataFrame({"Tiempo": t, "Temperatura": temp})

        if dark:
            face = "#0b1220"; color_line = "#ff6b6b"; color_goal = "#4cc9f0"; text_color = "white"; grid_alpha = 0.16
        else:
            face = "white"; color_line = "#ff6b00"; color_goal = "#2bbf7f"; text_color = "black"; grid_alpha = 0.12

        # Animate with guaranteed <= 2.8s; if rendering slower, abort and show final
        max_anim_time = 2.8
        frames = 30
        sleep_per_frame = max_anim_time / frames
        indices = np.linspace(5, len(df), frames, dtype=int)

        start_time = time.time()
        aborted = False
        for idx in indices:
            tt = df["Tiempo"].values[:idx]
            tp = df["Temperatura"].values[:idx]
            fig, ax = plt.subplots(figsize=(6.2, 3.2), tight_layout=True)
            fig.patch.set_facecolor(face); ax.set_facecolor(face)
            ax.plot(tt, tp, color=color_line, linewidth=2, label=f"Temperatura ({tipo})")
            ax.axhline(temp_f, color=color_goal, linestyle="--", linewidth=1.25, label=f"Objetivo {temp_f} °C")
            ax.set_title(f"Temperatura vs Tiempo — {tipo}", color=text_color, fontsize=12)
            ax.set_xlabel("Tiempo (segundos)", color=text_color, fontsize=10)
            ax.set_ylabel("Temperatura (°C)", color=text_color, fontsize=10)
            ax.tick_params(colors=text_color); ax.grid(alpha=grid_alpha); ax.legend(fontsize=9)
            placeholder_plot.pyplot(fig); plt.close(fig)

            elapsed = time.time() - start_time
            if elapsed + sleep_per_frame > max_anim_time:
                aborted = True
                break
            time.sleep(sleep_per_frame)

        if aborted:
            fig_final, ax = plt.subplots(figsize=(6.2, 3.2), tight_layout=True)
            fig_final.patch.set_facecolor(face); ax.set_facecolor(face)
            ax.plot(df["Tiempo"], df["Temperatura"], color=color_line, linewidth=2, label=f"Temperatura ({tipo})")
            ax.axhline(temp_f, color=color_goal, linestyle="--", linewidth=1.25, label=f"Objetivo {temp_f} °C")
            ax.set_title(f"Temperatura vs Tiempo — {tipo}", color=text_color, fontsize=12)
            ax.set_xlabel("Tiempo (segundos)", color=text_color, fontsize=10)
            ax.set_ylabel("Temperatura (°C)", color=text_color, fontsize=10)
            ax.tick_params(colors=text_color); ax.grid(alpha=grid_alpha); ax.legend(fontsize=9)
            placeholder_plot.pyplot(fig_final); plt.close(fig_final)

if st.session_state.history:
    st.markdown("---")
    st.subheader("Historial de simulaciones (últimas 10)")
    df_hist = pd.DataFrame(st.session_state.history).head(10)
    st.table(df_hist[["timestamp", "tipo", "cantidad_ml", "temp_inicial_C", "intensidad", "tiempo_min"]])
