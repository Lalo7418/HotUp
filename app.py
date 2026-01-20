import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime
from utils import cargar_csv, generar_grafica

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
if "history" not in st.session_state:
    st.session_state["history"] = []
if "show_history" not in st.session_state:
    st.session_state["show_history"] = False

def toggle_theme():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]

def toggle_history():
    st.session_state["show_history"] = not st.session_state["show_history"]

theme_dark = st.session_state["dark_mode"]

if theme_dark:
    css = """
    <style>
    :root{
        --bg:#0f1724;
        --topbar:#09111a;
        --card:#0b1220;
        --accent:#ff6b6b;
        --accent-2:#4cc9f0;
        --muted:#9aa4b2;
    }
    body {background: var(--bg); color: #e6eef6;}
    .topbar {
        background: linear-gradient(90deg, rgba(16,22,30,1), rgba(10,12,18,1));
        padding: 18px 24px;
        border-radius: 8px;
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:12px;
    }
    .topbar .title {font-size:34px; font-weight:800; color:#fff; margin:0;}
    .topbar .subtitle {font-size:13px; color:var(--muted); margin:0;}
    .card {background: var(--card); border-radius:10px; padding:12px; color:#e6eef6;}
    .input-summary {background: rgba(255,255,255,0.02); padding:8px; border-radius:8px; color:#e6eef6;}
    .btn-light {background:#1f2a36; color:#e6eef6; padding:6px 10px; border-radius:8px;}
    .history-card {background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:12px; border-radius:8px;}
    </style>
    """
else:
    css = """
    <style>
    :root{
        --bg:#fff7ed;
        --topbar:#fff1e6;
        --card:#fff6ea;
        --accent:#ff6b00;
        --accent-2:#2bbf7f;
        --muted:#6b6b6b;
    }
    body {background: var(--bg); color: #0e1b2b;}
    .topbar {
        background: linear-gradient(90deg, #fff4e6, #fff9f0);
        padding: 18px 24px;
        border-radius: 8px;
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
    }
    .topbar .title {font-size:34px; font-weight:800; color:#0e1b2b; margin:0;}
    .topbar .subtitle {font-size:13px; color:var(--muted); margin:0;}
    .card {background: var(--card); border-radius:10px; padding:12px; color:#0e1b2b;}
    .input-summary {background: rgba(0,0,0,0.02); padding:8px; border-radius:8px; color:#0e1b2b;}
    .btn-light {background:#ffdcb3; color:#0e1b2b; padding:6px 10px; border-radius:8px;}
    .history-card {background:linear-gradient(180deg, #fffdfa, #fff9f0); padding:12px; border-radius:8px;}
    </style>
    """

st.markdown(css, unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="topbar">
      <div>
        <div class="title">HeatUp</div>
        <div class="subtitle">Calculadora para calentar líquidos en la cocina</div>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <div>
          <form>
            <select id="mode_select" disabled style="padding:6px; border-radius:6px;">
              <option>{'Oscuro' if theme_dark else 'Claro'}</option>
            </select>
          </form>
        </div>
        <div>
          <button onclick="document.querySelector('#toggle-theme').click()" class="btn-light">Modo {'Oscuro' if not theme_dark else 'Claro'}</button>
        </div>
        <div>
          <button onclick="document.querySelector('#toggle-history').click()" class="btn-light">Historial</button>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.button("toggle-theme", key="toggle-theme", on_click=toggle_theme, help="Alternar tema (oculto)")
st.button("toggle-history", key="toggle-history", on_click=toggle_history, help="Mostrar / ocultar historial (oculto)")

modo = st.selectbox("Modo", ["Básico", "Avanzado"], index=0, help="Selecciona Básico o Avanzado")

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

        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "tipo": tipo,
            "volumen_ml": volumen,
            "temp_inicial_C": temp_inicial,
            "intensidad": fuego if fuego else "",
            "tiempo_min": round(tiempo_real, 3)
        }
        st.session_state["history"].insert(0, record)
        if len(st.session_state["history"]) > 50:
            st.session_state["history"] = st.session_state["history"][:50]

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
            grid_alpha = 0.16
            face = "#0b1220"
        else:
            color_line = "#ff6b00"
            color_goal = "#2bbf7f"
            text_color = "#0e1b2b"
            grid_alpha = 0.12
            face = "white"

        frames = 36
        indices = np.linspace(5, t.size, frames, dtype=int)

        placeholder = st.empty()
        for idx in indices:
            tt = t[:idx]
            tp = temp[:idx]
            fig, ax = plt.subplots(figsize=(6.2, 3.2), tight_layout=True)
            fig.patch.set_facecolor(face)
            ax.set_facecolor(face)
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
            time.sleep(0.004)

if st.session_state["show_history"]:
    st.markdown('<div class="history-card">', unsafe_allow_html=True)
    st.markdown("### Historial de simulaciones recientes")
    if st.session_state["history"]:
        history_df = st.session_state["history"]
        st.table(history_df[:10])
        if st.button("Borrar historial"):
            st.session_state["history"] = []
    else:
        st.markdown("No hay simulaciones guardadas.")
    st.markdown('</div>', unsafe_allow_html=True)
