import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from utils import cargar_csv, generar_grafica

st.set_page_config(page_title="HeatUp", layout="wide")

st.markdown(
    """
    <style>
    :root{
        --bg:#0f1724;
        --card:#0b1220;
        --accent:#ff6b6b;
        --accent-2:#4cc9f0;
        --muted:#9aa4b2;
        --glass: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    }
    body {background: var(--bg); color: #e6eef6;}
    .stApp .block-container{padding-top:1rem; padding-left:2rem; padding-right:2rem;}
    .title {font-size:34px; font-weight:700; color: #ffffff; margin-bottom:0.1rem;}
    .subtitle {color: var(--muted); margin-top:0; margin-bottom:0.6rem;}
    .card {
        background: var(--card);
        border-radius:12px;
        padding:14px;
        box-shadow: 0 6px 18px rgba(2,6,23,0.6);
    }
    .metric-key {color:var(--muted); font-size:12px;}
    .input-summary {background: var(--glass); padding:10px; border-radius:8px; color:#e6eef6;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">HeatUp</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Calculadora para calentar líquidos en la cocina</div>', unsafe_allow_html=True)
st.markdown("---")

modo = st.sidebar.selectbox("Selecciona modo", ["Básico", "Avanzado"])

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

left, right = st.columns([1, 1])

with left:
    with st.form("calculo_form"):
        st.markdown('### Parámetros', unsafe_allow_html=True)
        tipo = st.selectbox("Tipo de líquido", list(liquidos.keys()))
        volumen = st.number_input("Cantidad (ml)", min_value=1, value=250, step=50, format="%d")
        if modo == "Básico":
            fuego = st.selectbox("Intensidad del fuego", ["Bajo", "Medio", "Alto"])
            temp_inicial = 25.0
        else:
            temp_inicial = st.number_input("Temperatura inicial (°C)", min_value=-10.0, value=25.0, step=1.0)
            fuego = None
        calcular = st.form_submit_button("Calcular Tiempo")

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Resumen de entrada")
    resumen_area = st.empty()
    st.markdown("### Resultado")
    tiempo_area = st.empty()
    st.markdown("### Simulación")
    plot_area = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

if calcular:
    if volumen <= 0:
        st.error("La cantidad debe ser mayor que 0 ml.")
    else:
        temp_obj = liquidos[tipo]["temp_obj"]
        tiempo_base = (volumen * (temp_obj - temp_inicial)) / 8000.0
        if modo == "Básico":
            factor = fuego_factor.get(fuego, 1.0)
        else:
            factor = 1.0
        tiempo_real = max(tiempo_base * factor, 0.01)
        minutos = int(tiempo_real)
        segundos = int(round((tiempo_real - minutos) * 60))

        resumen_markdown = f"""
        <div class="input-summary">
        <strong>Tipo de líquido:</strong> {tipo}  
        <strong>Cantidad:</strong> {volumen} ml  
        <strong>Temperatura inicial:</strong> {temp_inicial} °C  
        """
        if modo == "Básico":
            resumen_markdown += f"<strong>Intensidad del fuego:</strong> {fuego}  "
        resumen_markdown += "</div>"

        resumen_area.markdown(resumen_markdown, unsafe_allow_html=True)
        tiempo_area.metric("Tiempo estimado", f"{tiempo_real:.2f} min", delta=f"{minutos}m {segundos}s")

        total_seg = max(tiempo_real * 60.0, 1.0)
        t = np.linspace(0, total_seg, 300)
        k = -np.log(0.01) / total_seg
        temp = temp_obj - (temp_obj - temp_inicial) * np.exp(-k * t)

        color_line = "#ff6b6b"
        color_goal = "#4cc9f0"

        frames = 80
        indices = np.linspace(1, t.size, frames, dtype=int)
        last_fig = None
        for idx in indices:
            tt = t[:idx]
            tp = temp[:idx]
            fig, ax = plt.subplots(figsize=(6.4, 3.2), tight_layout=True)
            ax.plot(tt, tp, color=color_line, linewidth=2)
            ax.axhline(temp_obj, color=color_goal, linestyle="--", linewidth=1.25)
            ax.set_title("Temperatura vs Tiempo", color="#e6eef6", fontsize=12)
            ax.set_xlabel("Tiempo (segundos)", color="#cbd7e8", fontsize=10)
            ax.set_ylabel("Temperatura (°C)", color="#cbd7e8", fontsize=10)
            ax.tick_params(colors="#9aa4b2")
            ax.grid(alpha=0.2)
            plot_area.pyplot(fig)
            plt.close(fig)
            last_fig = fig
            time.sleep(0.02)

        try:
            df = cargar_csv("example_data.csv")
            st.markdown("### Historial (ejemplo)")
            fig_hist = generar_grafica(df, figsize=(6.4, 2.8))
            st.pyplot(fig_hist)
            plt.close(fig_hist)
        except Exception:
            pass

st.markdown("---")
