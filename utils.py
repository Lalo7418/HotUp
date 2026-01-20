import matplotlib.pyplot as plt

def generar_grafica(df, dark=False):
    fig, ax = plt.subplots(figsize=(7, 3.5), tight_layout=True)

    if dark:
        fig.patch.set_facecolor("#020617")
        ax.set_facecolor("#020617")
        color = "#fb7185"
        text = "#e5e7eb"
    else:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        color = "#ea580c"
        text = "#1e293b"

    ax.plot(df.iloc[:,0], df.iloc[:,1], color=color, linewidth=2)
    ax.set_xlabel("Tiempo (s)", color=text)
    ax.set_ylabel("Temperatura (°C)", color=text)
    ax.tick_params(colors=text)
    ax.grid(alpha=0.15)

    return fig
