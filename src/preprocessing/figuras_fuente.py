"""
Figuras fuente - South German Credit
Unidad II: Diagnostico del conjunto de datos del Proyecto Integrador.

Fuente canonica y preservada del codigo que genera las 5 figuras del
informe docs/analisis/exploracion_tecnica.md. Cada figura vive en su
propia funcion; los comentarios "TRASPASO Pandas -> Matplotlib"
marcan el punto exacto donde un objeto de Pandas (Series/DataFrame)
se entrega a Matplotlib para dibujar.

Uso:
    py src/preprocessing/figuras_fuente.py               # figuras oficiales
    py src/preprocessing/figuras_fuente.py <carpeta>     # carpeta alternativa
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAW = os.path.join("data", "raw", "SouthGermanCredit.asc")
OUT_DIR = os.path.join("docs", "analisis", "figuras")

# Paleta compartida
AZUL = "#4C72B0"
ROJO = "#C44E52"
VERDE = "#55A868"


def fig_hist_monto(df, outdir):
    """Fig. 1 - Histograma del monto del credito (hoehe)."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    # TRASPASO Pandas -> Matplotlib #1: Series df["hoehe"] -> ax.hist
    ax.hist(df["hoehe"], bins=25, color=AZUL, edgecolor="white")
    # TRASPASO Pandas -> Matplotlib #2: escalar median() -> ax.axvline
    ax.axvline(df["hoehe"].median(), color=ROJO, linestyle="--",
               label=f"Mediana = {df['hoehe'].median():.0f} DM")
    ax.set_title("Histograma del monto del credito (hoehe)")
    ax.set_xlabel("Monto del credito (DM, transformacion monotona)")
    ax.set_ylabel("Numero de creditos")
    ax.legend()
    fig.tight_layout()
    destino = os.path.join(outdir, "fig1_hist_monto.png")
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return destino


def fig_boxplots(df, outdir):
    """Fig. 2 - Boxplots de las variables numericas relevantes."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, col, titulo in zip(axes,
                               ["laufzeit", "hoehe", "alter"],
                               ["Duracion (meses)", "Monto (DM)", "Edad (anios)"]):
        # TRASPASO Pandas -> Matplotlib #3: Series df[col] -> ax.boxplot
        ax.boxplot(df[col], vert=True)
        ax.set_title(f"Boxplot: {titulo}")
        ax.set_ylabel(titulo)
    fig.suptitle("Diagramas de caja de las variables numericas relevantes", y=1.02)
    fig.tight_layout()
    destino = os.path.join(outdir, "fig2_boxplot_numericas.png")
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return destino


def fig_barras_historial(df, outdir):
    """Fig. 3 - Porcentaje de creditos 'good' por historial crediticio (moral)."""
    # --- aqui Pandas calcula TODO; Matplotlib solo dibuja el resultado ---
    tasa = df.groupby("moral")["kredit"].mean() * 100      # % good por categoria
    conteo = df["moral"].value_counts().sort_index()       # n por categoria
    etiquetas = {
        0: "0 Antecedente\nde atraso",
        1: "1 Cuenta critica/\notros bancos",
        2: "2 Sin creditos/\npagados puntual",
        3: "3 Existentes pagados\npuntual hasta hoy",
        4: "4 Todos los creditos\nde este banco OK",
    }
    fig, ax = plt.subplots(figsize=(8, 4.5))
    # TRASPASO Pandas -> Matplotlib #4: tasa.index (etiquetas) + tasa.values (alturas)
    barras = ax.bar([etiquetas[i] for i in tasa.index], tasa.values,
                    color=[ROJO if v < 50 else VERDE for v in tasa.values])
    # TRASPASO Pandas -> Matplotlib #5: conteo.values -> anotaciones n=...
    for barra, n in zip(barras, conteo.values):
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 2,
                f"n={n}", ha="center", fontsize=8)
    ax.set_title("Porcentaje de creditos 'good' por historial crediticio (moral)")
    ax.set_xlabel("Historial crediticio (moral)")
    ax.set_ylabel("% de creditos good")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    destino = os.path.join(outdir, "fig3_barras_riesgo_historial.png")
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return destino


def fig_dispersion(df, outdir):
    """Fig. 4 - Dispercion: duracion vs monto, coloreada por resultado."""
    # --- Pandas filtra las filas por clase (mascara booleana) ---
    good = df[df["kredit"] == 1]
    bad = df[df["kredit"] == 0]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    # TRASPASO Pandas -> Matplotlib #6: 4 Series (x,y good + x,y bad) -> ax.scatter
    ax.scatter(good["laufzeit"], good["hoehe"], alpha=0.55, label="good", s=25)
    ax.scatter(bad["laufzeit"], bad["hoehe"], alpha=0.55, label="bad", s=25)
    ax.set_title("Dispercion: duracion vs monto del credito")
    ax.set_xlabel("Duracion del credito (meses)")
    ax.set_ylabel("Monto del credito (DM)")
    ax.legend(title="credit_risk")
    fig.tight_layout()
    destino = os.path.join(outdir, "fig4_dispersion_monto_plazo.png")
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return destino


def fig_correlacion(df, outdir):
    """Fig. 5 - Matriz de correlacion (variables numericas + objetivo)."""
    # --- Pandas calcula la matriz 4x4 de correlaciones ---
    corr = df[["laufzeit", "hoehe", "alter", "kredit"]].corr()
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    # TRASPASO Pandas -> Matplotlib #7: DataFrame corr -> imshow (matriz de calor)
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns)
    ax.set_yticks(range(len(corr)), corr.columns)
    # Lectura inversa de la matriz de Pandas (.iloc) para anotar cada celda
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                    color="white" if abs(corr.iloc[i, j]) > 0.5 else "black",
                    fontsize=9)
    ax.set_title("Matriz de correlacion (variables numericas + objetivo)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    destino = os.path.join(outdir, "fig5_correlacion.png")
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return destino


def main(outdir=OUT_DIR):
    os.makedirs(outdir, exist_ok=True)
    df = pd.read_csv(RAW, sep=" ")
    entregas = [
        fig_hist_monto(df, outdir),
        fig_boxplots(df, outdir),
        fig_barras_historial(df, outdir),
        fig_dispersion(df, outdir),
        fig_correlacion(df, outdir),
    ]
    for ruta in entregas:
        print("Figura generada:", ruta)
    return entregas


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else OUT_DIR)
