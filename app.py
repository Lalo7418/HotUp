import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from utils import cargar_csv, generar_grafica

st.set_page_config(page_title="HeatUp - Poster Digital", layout="wide")

st.title("HeatUp")
st.subheader("Calculadora simple para calentar líquidos en la cocina")

st.markdown("""
## Descripción  
HeatUp permite estimar cuánto tiempo tarda un líquido común de cocina en calentarse,
sin necesidad de datos técnicos como potencia o temperaturas exactas.  

Solo elige el tipo de líquido, la cantidad y la intensidad del fuego.
""")

st.header("Calculadora para Cocina (Modo Simplificado)")

liquidos = {
    "Agua": {"temp_obj": 100},
    "Leche": {"temp_obj": 90},
    "Caldo / Sopa": {"temp_obj": 95},
    "Café frío para recalentar": {"temp_obj": 75},
    "Chocolate caliente": {"temp_obj": 85}
}

fuego_factor = {
    "Bajo": 1.6,
    "Medio": 1.0,
    "Alto": 0.7
}

with st.form("calculo_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo = st.selectbox("Tipo de líquido", list(liquidos.keys()))
        volumen = st.number_input("Cantidad (ml)", min_value=1, value=250, step=50)
    with col2:
        fuego = st.selectbox("Intensidad del fuego", ["Bajo", "Medio", "Alto"])
        temp_inicial = st.number_input("Temperatura inicial (°C)", min_value=-10.0, value=25.0, step=1.0)
    with col3:
        modelo = st.radio("Modelo de calentamiento", ("Lineal (simple)", "Newton (más realista)"))
        calcular = st.form_submit_button("Calcular Tiempo")

if calcular:
    if volumen <= 0:
        st.error("La cantidad debe ser mayor que 0 ml.")
    else:
        temp_obj = liquidos[tipo]["temp_obj"]
        factor = fuego_factor[fuego]

        tiempo_base = (volumen * (temp_obj - temp_inicial)) / 8000.0
        tiempo_real = max(tiempo_base * factor, 0.01)

        minutos = int(tiempo_real)
        segundos = int(round((tiempo_real - minutos) * 60))

        st.success(f"**Tiempo estimado:** {tiempo_real:.2f} minutos ({minutos} min {segundos} s)")

        st.header("Simulación de calentamiento")
        total_seg = max(tiempo_real * 60.0, 1.0)
        t = np.linspace(0, total_seg, 300)

        if modelo.startswith("Lineal"):
            temp = temp_inicial + (t / total_seg) * (temp_obj - temp_inicial)
        else:
            k = -np.log(0.01) / total_seg
            temp = temp_obj - (temp_obj - temp_inicial) * np.exp(-k * t)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(t, temp, linewidth=2, label="Temperatura (°C)")
        ax.axhline(temp_obj, color="tab:orange", linestyle="--", label=f"Objetivo {temp_obj}°C")
        ax.set_title("Simulación de Temperatura vs Tiempo")
        ax.set_xlabel("Tiempo (segundos)")
        ax.set_ylabel("Temperatura (°C)")
        ax.grid(True)
        ax.legend()

        st.pyplot(fig)
        plt.close(fig)
        try:
            df = cargar_csv("example_data.csv")
            st.subheader("Historial (ejemplo)")
            fig_hist = generar_grafica(df)
            st.pyplot(fig_hist)
            plt.close(fig_hist)
        except Exception:
            st.info("No hay datos históricos disponibles o hubo un error cargando example_data.csv.")

st.markdown("---")
st.markdown("Proyecto HeatUp")
