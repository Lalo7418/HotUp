import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_data
def cargar_csv(archivo: str) -> pd.DataFrame:
    """
    Carga un CSV y lo devuelve como DataFrame.
    """
    df = pd.read_csv(archivo)
    return df

def generar_grafica(df: pd.DataFrame, figsize=(6.0, 2.8)) -> plt.Figure:
    """
    Genera una figura matplotlib a partir de un DataFrame.
    Permite especificar tamaño para evitar imágenes gigantes en la UI.
    """
    fig, ax = plt.subplots(figsize=figsize, tight_layout=True)
    ax.plot(df.iloc[:, 0], df.iloc[:, 1], marker="o", linewidth=1.6, color="#1f77b4")
    ax.set_title("Historial de Calentamientos", fontsize=11)
    ax.set_xlabel(df.columns[0], fontsize=9)
    ax.set_ylabel(df.columns[1], fontsize=9)
    ax.grid(alpha=0.3)
    return fig
