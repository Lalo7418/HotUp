import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime
from utils import cargar_csv, generar_grafica

# Estado inicial
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

# CSS general y sticky topbar (aplica al primer bloque dentro del bloque de la app)
css = """
<style>
/* Topbar (sticky) */
.stApp .block-container > div:first-child {
  position: sticky;
  top: 0;
  z-index: 9999;
}

/* Temas y paleta */
:root {
  --cook-cream: #fff7ed;
  --cook-sauce: #ff6b00;
  --cook-basil: #2bbf7f;
  --cook-lemon: #ffd60a;
  --dark-bg: #0f1724;
  --dark-top: #09111a;
  --card-dark: #0b1220;
}

/* Topbar styling common */
.topbar {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 14px 20px;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
}

/* Light topbar */
.light-topbar {
  background: linear-gradient(90deg, #fff4e6, #fff9f0);
  color: #0e1b2b;
  box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}

/* Dark topbar */
.dark-topbar {
  background: linear-gradient(90deg, rgba(16,22,30,1), rgba(10,12,18,1));
  color: #e6eef6;
}

/* Title area */
.topbar .title { font-size:28px; font-weight:800; margin:0; }
.topbar .subtitle { font-size:13px; margin:0; opacity:0.9; }

/* Controls group */
.topbar .controls { display:flex; gap:8px; align-items:center; }

/* Small button */
.btn {
  padding:8px 12px;
  border-radius:8px;
  border: none;
  cursor: pointer;
  font-weight:600;
}

/* Light / dark variants for btn */
.btn-light {
  background: #ffdcb3;
  color: #0e1b2b;
}
.btn-accent {
  background: var(--cook-sauce);
  color: white;
}
.btn-ghost {
  background: transparent;
  color: inherit;
  border: 1px solid rgba(0,0,0,0.06);
}

/* Small note */
.small-note { font-size:13px; color:inherit; opacity:0.85; margin-top:6px; text-align:center; }

/* Card */
.card {
  border-radius:10px;
  padding:14px;
}
.light-card { background: #fff6ea; color:#0e1b2b; box-shadow: 0 6px 18px rgba(0,0,0,0.03); }
.dark-card { background: #0b1220; color:#e6eef6; }

/* History table compact */
.history-table th, .history-table td { padding:6px 8px; font-size:13px; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Topbar: usamos un container de Streamlit para que widgets dentro funcionen correctamente
topbar_class = "dark-topbar" if theme_dark else "light-topbar"
with st.container():
    cols = st.columns([1, 1, 1])
    # Left: title+subtitle
    with cols[0]:
        st.markdown(f'<div class="topbar {topbar_class}">'
                    f'<div>'
                    f'<div class="title">HeatUp</div>'
                    f'<div class="subtitle">Calculadora para calentar líquidos en la cocina</div>'
                    f'</div>',
                    unsafe_allow_html=True)
    # Middle: mode selector (visible in topbar)
    with cols[1]:
        mode = st.selectbox("Modo", ["Básico", "Avanzado"], index=0, key="mode_top")
    # Right: theme toggle & history toggle buttons
    with cols[2]:
        col_btns = st.columns([1,1,1])
        if st.button("Oscuro/Claro", key="theme_btn"):
            toggle_theme()
            st.experimental_rerun()
        if st.button("Historial", key="history_btn"):
            toggle_history()
        if st.button("Exportar CSV", key="export_btn"):
            # Export current history as CSV if any
            if st.session_state["history"]:
                import pandas as pd, io
                df = pd.DataFrame(st.session_state["history"])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Descargar historial (.csv)", csv, "heatup_history.csv", "text/csv")
            else:
                st.info("No hay historial para exportar.")
    # close the topbar div
    st.markdown("</div>", unsafe_allow_html=True)

# Brief instruction under topbar
if theme_dark:
    st.markdown('<div class="small-note" style="color:#9aa4b2">Cambia el modo en la barra superior. Rellena los parámetros y pulsa "Calcular Tiempo".</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="small-note" style="color:#54606a">Cambia el modo en la barra superior. Rellena los parámetros y pulsa "Calcular Tiempo".</div>', unsafe_allow_html=True)

# Parámetros (justo debajo del topbar)
liquidos = {
    "Agua": {"temp_obj": 100},
    "Leche": {"temp_obj": 90},
    "Caldo / Sopa": {"temp_obj": 95},
    "Café (recalentar)": {"temp_obj": 75},
    "Chocolate caliente": {"temp_obj": 85}
}
fuego_factor = {"Bajo": 1.6, "Medio": 1.0, "Alto": 0.7}

with st.form("calculo_form", clear_on_submit=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        tipo = st.selectbox("Tipo de líquido", list(liquidos.keys()))
        volumen = st.number_input("Cantidad (ml)", min_value=1, value=250, step=50, format="%d")
    with c2:
        if mode == "Básico":
            fuego = st.selectbox("Intensidad del fuego", ["Bajo", "Medio", "Alto"])
            temp_inicial = 25.0
        else:
            fuego = None
            temp_inicial = st.number_input("Temperatura inicial (°C)", min_value=-10.0, value=25.0, step=1.0)
    with c3:
        submit = st.form_submit_button("Calcular Tiempo", use_container_width=True)

# Lógica de cálculo y visualización
if submit:
    if volumen <= 0:
        st.error("La cantidad debe ser mayor que 0 ml.")
    else:
        temp_obj = liquidos[tipo]["temp_obj"]
        tiempo_base = (volumen * (temp_obj - temp_inicial)) / 8000.0
        factor = fuego_factor.get(fuego, 1.0)
        if mode == "Avanzado":
            factor = 1.0
        tiempo_real = max(tiempo_base * factor, 0.01)  # minutos
        minutos = int(tiempo_real)
        segundos = int(round((tiempo_real - minutos) * 60))

        # Guardar en historial (más reciente primero)
        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "tipo": tipo,
            "volumen_ml": volumen,
            "temp_inicial_C": temp_inicial,
            "intensidad": fuego if fuego else "",
            "tiempo_min": round(tiempo_real, 3)
        }
        st.session_state["history"].insert(0, record)
        if len(st.session_state["history"]) > 200:
            st.session_state["history"] = st.session_state["history"][:200]

        # Mostrar resumen de inputs
        resumen = f"**Tipo:** {tipo}   •   **Cantidad:** {volumen} ml   •   **Temp. inicial:** {temp_inicial} °C"
        if mode == "Básico":
            resumen += f"   •   **Intensidad:** {fuego}"
        st.markdown(f'<div class="card {"dark-card" if theme_dark else "light-card"}">{resumen}</div>', unsafe_allow_html=True)
        st.metric("Tiempo estimado", f"{tiempo_real:.2f} min", delta=f"{minutos}m {segundos}s")

        # Simulación (Newton), animación siempre < 2.5s
        total_seg = max(tiempo_real * 60.0, 1.0)
        t = np.linspace(0, total_seg, 300)
        k = -np.log(0.01) / total_seg
        temp = temp_obj - (temp_obj - temp_inicial) * np.exp(-k * t)

        if theme_dark:
            color_line = "#ff6b6b"
            color_goal = "#4cc9f0"
            text_color = "white"
            facecolor = "#0b1220"
            grid_alpha = 0.16
        else:
            color_line = "#ff6b00"
            color_goal = "#2bbf7f"
            text_color = "#0e1b2b"
            facecolor = "white"
            grid_alpha = 0.12

        # Animación controlada: duración total limitada a 2.5s
        frames = 40
        total_anim_time = 2.5
        sleep_per_frame = total_anim_time / frames
        indices = np.linspace(5, t.size, frames, dtype=int)
        plot_placeholder = st.empty()
        for idx in indices:
            tt = t[:idx]
            tp = temp[:idx]
            fig, ax = plt.subplots(figsize=(6.2, 3.2), tight_layout=True)
            fig.patch.set_facecolor(facecolor)
            ax.set_facecolor(facecolor)
            ax.plot(tt, tp, color=color_line, linewidth=2, label=f"Temperatura ({tipo})")
            ax.axhline(temp_obj, color=color_goal, linestyle="--", linewidth=1.25, label=f"Objetivo {temp_obj} °C")
            ax.set_title(f"Temperatura vs Tiempo — {tipo}", color=text_color, fontsize=12)
            ax.set_xlabel("Tiempo (segundos)", color=text_color, fontsize=10)
            ax.set_ylabel("Temperatura (°C)", color=text_color, fontsize=10)
            ax.tick_params(colors=text_color)
            ax.grid(alpha=grid_alpha)
            ax.legend(fontsize=9)
            plot_placeholder.pyplot(fig)
            plt.close(fig)
            time.sleep(sleep_per_frame)

# Historial (se muestra cuando el usuario pulsa el botón Historial en la topbar)
if st.session_state["show_history"]:
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<div class="card" style="padding:10px">', unsafe_allow_html=True)
    st.markdown("### Historial de simulaciones recientes")
    if st.session_state["history"]:
        import pandas as pd
        df_hist = pd.DataFrame(st.session_state["history"])
        # Mostrar tabla compacta (hasta 20 filas)
        st.table(df_hist[["timestamp", "tipo", "volumen_ml", "temp_inicial_C", "intensidad", "tiempo_min"]].head(20))
        if st.button("Borrar historial"):
            st.session_state["history"] = []
            st.experimental_rerun()
    else:
        st.markdown("No hay simulaciones guardadas.")
    st.markdown("</div>", unsafe_allow_html=True)
