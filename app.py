import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

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
    tipo = st.selectbox("Tipo de líquido", list(liquidos.keys()))
    volumen = st.number_input("Cantidad (ml)", min_value=50, value=250)
    fuego = st.selectbox("Intensidad del fuego", ["Bajo", "Medio", "Alto"])

    calcular = st.form_submit_button("Calcular Tiempo")

if calcular:
    temp_inicial = 25
    temp_obj = liquidos[tipo]["temp_obj"]
    factor = fuego_factor[fuego]

    tiempo_base = (volumen * (temp_obj - temp_inicial)) / 8000
    tiempo_real = tiempo_base * factor

    tiempo_min = tiempo_real

    st.success(f"**Tiempo estimado:** {tiempo_min:.1f} minutos")
    st.header("Simulación de calentamiento")

    t = np.linspace(0, tiempo_real * 60, 60)
    temp = temp_inicial + (t / (tiempo_real * 60)) * (temp_obj - temp_inicial)

    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(t, temp, linewidth=2)
    ax.set_title("Simulación de Temperatura vs Tiempo")
    ax.set_xlabel("Tiempo (segundos)")
    ax.set_ylabel("Temperatura (°C)")
    ax.grid(True)

    st.pyplot(fig)

st.markdown("---")
st.markdown("Proyecto HeatUp")
