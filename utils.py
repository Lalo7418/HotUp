import matplotlib.pyplot as plt

def generar_grafica(df, dark: bool):
    fig, ax = plt.subplots(figsize=(7, 3.5), tight_layout=True)

    if dark:
        fig.patch.set_facecolor("#020617")
        ax.set_facecolor("#020617")
        color = "#fb7185"   # warm pink/tomato accent
        text = "#f8fafc"
    else:
        fig.patch.set_facecolor("#fff7ed")
        ax.set_facecolor("#fff7ed")
        color = "#7c2d12"
        text = "#431407"

    ax.plot(df.iloc[:, 0], df.iloc[:, 1], linewidth=2.5, color=color)
    ax.set_xlabel("Tiempo (s)", color=text)
    ax.set_ylabel("Temperatura (°C)", color=text)
    ax.tick_params(colors=text)
    ax.grid(alpha=0.15)
    return fig
