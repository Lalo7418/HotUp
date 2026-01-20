import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_data
def cargar_csv(archivo: str):
    return pd.read_csv(archivo)

def generar_grafica(df, figsize=(6.4, 2.8)):
    fig, ax = plt.subplots(figsize=figsize, tight_layout=True)
    cols = list(df.columns)
    x_label = cols[0]
    y_label = cols[1]
    if x_label.lower() in ["tiempo_minutos", "tiempo", "minutos"]:
        x_label_f = "Tiempo (minutos)"
    else:
        x_label_f = x_label
    if y_label.lower() in ["uso_calentador", "uso", "uso_calent"]:
        y_label_f = "Uso del calentador"
    else:
        y_label_f = y_label
    ax.plot(df.iloc[:, 0], df.iloc[:, 1], marker="o", linewidth=1.6, color="#1f77b4")
    ax.set_title("Historial de Calentamientos", color="#e6eef6", fontsize=11)
    ax.set_xlabel(x_label_f, color="#cbd7e8", fontsize=9)
    ax.set_ylabel(y_label_f, color="#cbd7e8", fontsize=9)
    ax.tick_params(colors="#9aa4b2")
    ax.grid(alpha=0.2)
    return fig
