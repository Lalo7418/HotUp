import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_data
def cargar_csv(archivo: str):
    return pd.read_csv(archivo)

def generar_grafica(df, figsize=(5.8, 2.2), theme_dark=True):
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
    if theme_dark:
        fig.patch.set_facecolor("#0b1220")
        ax.set_facecolor("#0b1220")
        text_color = "white"
        line_color = "#ffd166"
    else:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        text_color = "black"
        line_color = "#1f77b4"
    ax.plot(df.iloc[:, 0], df.iloc[:, 1], marker="o", linewidth=1.6, color=line_color)
    ax.set_title("Historial de Calentamientos", color=text_color, fontsize=11)
    ax.set_xlabel(x_label_f, color=text_color, fontsize=9)
    ax.set_ylabel(y_label_f, color=text_color, fontsize=9)
    ax.tick_params(colors=text_color)
    ax.grid(alpha=0.12)
    return fig
