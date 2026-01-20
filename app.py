import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from utils import cargar_csv, generar_grafica

st.set_page_config(page_title="HeatUp - Poster Digital", layout="wide")

st.markdown(
    """
    <style>
    .title {text-align: center; font-size: 34px; font-weight:700;}
    .subtitle {text-align: center; color: #6c757d;}
    .card {background: linear-gradient(90deg,#ffffffcc,#f7f9fccc);
           border-radius: 10px; padding: 12px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">HeatUp</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Calculadora para calentar líquidos en la cocina</div>', unsafe_allow_html=True)
st.markdown("---")

modo = st.sidebar.selectbox("Selecciona modo", ["Básico", "Avanzado"])
st.sidebar.markdown("Proyecto HeatUp · Demo para presentación")
st.sidebar.markdown("Inputs y gráficos optimizados para presentación")

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
        st.markdown("### Parámetros")
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
    st.markdown("### Resultado")
    tiempo_placeholder = st.empty()
    st.markdown("### Visualización")
    plot_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

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
        tiempo_placeholder.metric("Tiempo estimado", f"{tiempo_real:.2f} min", delta=f"{minutos}m {segundos}s")
        total_seg = max(tiempo_real * 60.0, 1.0)
        t = np.linspace(0, total_seg, 250)
        k = -np.log(0.01) / total_seg
        temp = temp_obj - (temp_obj - temp_inicial) * np.exp(-k * t)

        fig, ax = plt.subplots(figsize=(6.0, 3.5), tight_layout=True)
        ax.plot(t, temp, color="#d1495b", linewidth=2, label="Temperatura (°C)")
        ax.axhline(temp_obj, color="#0077b6", linestyle="--", linewidth=1.25, label=f"Objetivo {temp_obj}°C")
        ax.set_title("Simulación: Temperatura vs Tiempo", fontsize=12)
        ax.set_xlabel("Tiempo (segundos)", fontsize=10)
        ax.set_ylabel("Temperatura (°C)", fontsize=10)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=9)
        plot_placeholder.pyplot(fig)
        plt.close(fig)

        try:
            df = cargar_csv("example_data.csv")
            st.markdown("### Historial (ejemplo)")
            fig_hist = generar_grafica(df, figsize=(6.0, 2.8))
            st.pyplot(fig_hist)
            plt.close(fig_hist)
        except Exception:
            pass

st.markdown("---")
cols = st.columns(3)
cols[0].markdown("**HeatUp**")
cols[1].markdown("Versión demo")
cols[2].markdown("Autor: Proyecto")
