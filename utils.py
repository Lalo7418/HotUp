import pandas as pd
import matplotlib.pyplot as plt

def cargar_csv(archivo):
    df = pd.read_csv(archivo)
    return df

def generar_grafica(df):
    fig, ax = plt.subplots()
    ax.plot(df.iloc[:, 0], df.iloc[:, 1])
    ax.set_title("Historial de Calentamientos")
    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    return fig
