"""
Exploracion Tecnica - South German Credit
Unidad II: Diagnostico del conjunto de datos del Proyecto Integrador.

Genera las figuras de la seccion 7 (boxplots) y 8 (visualizaciones) en
docs/analisis/figuras/ y calcula los estadisticos usados en el informe
docs/analisis/exploracion_tecnica.md.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.join("docs", "analisis", "figuras")
RAW = os.path.join("data", "raw", "SouthGermanCredit.asc")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

df = pd.read_csv(RAW, sep=" ")
os.makedirs(BASE, exist_ok=True)


# ---------------------------------------------------------------- figuras
fig1, ax1 = plt.subplots(figsize=(8, 4.5))
ax1.hist(df["hoehe"], bins=25, color="#4C72B0", edgecolor="white")
ax1.axvline(df["hoehe"].median(), color="#C44E52", linestyle="--",
            label=f"Mediana = {df['hoehe'].median():.0f} DM")
ax1.set_title("Histograma del monto del credito (hoehe)")
ax1.set_xlabel("Monto del credito (DM, transformacion monotona)")
ax1.set_ylabel("Numero de creditos")
ax1.legend()
fig1.tight_layout()
fig1.savefig(os.path.join(BASE, "fig1_hist_monto.png"), dpi=150)
plt.close(fig1)

fig2, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, col, titulo in zip(axes,
                           ["laufzeit", "hoehe", "alter"],
                           ["Duracion (meses)", "Monto (DM)", "Edad (anios)"]):
    ax.boxplot(df[col], vert=True)
    ax.set_title(f"Boxplot: {titulo}")
    ax.set_ylabel(titulo)
fig2.suptitle("Diagramas de caja de las variables numericas relevantes", y=1.02)
fig2.tight_layout()
fig2.savefig(os.path.join(BASE, "fig2_boxplot_numericas.png"), dpi=150, bbox_inches="tight")
plt.close(fig2)

fig3, ax3 = plt.subplots(figsize=(8, 4.5))
tasa = df.groupby("moral")["kredit"].mean() * 100
conteo = df["moral"].value_counts().sort_index()
etiquetas = {
    0: "0 Antecedente\nde atraso",
    1: "1 Cuenta critica/\notros bancos",
    2: "2 Sin creditos/\npagados puntual",
    3: "3 Existentes pagados\npuntual hasta hoy",
    4: "4 Todos los creditos\nde este banco OK",
}
barras = ax3.bar([etiquetas[i] for i in tasa.index], tasa.values,
                 color=["#C44E52" if v < 50 else "#55A868" for v in tasa.values])
for barra, n in zip(barras, conteo.values):
    ax3.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 2,
             f"n={n}", ha="center", fontsize=8)
ax3.set_title("Porcentaje de creditos 'good' por historial crediticio (moral)")
ax3.set_xlabel("Historial crediticio (moral)")
ax3.set_ylabel("% de creditos good")
ax3.set_ylim(0, 100)
fig3.tight_layout()
fig3.savefig(os.path.join(BASE, "fig3_barras_riesgo_historial.png"), dpi=150)
plt.close(fig3)

fig4, ax4 = plt.subplots(figsize=(8, 4.5))
good = df[df["kredit"] == 1]
bad = df[df["kredit"] == 0]
ax4.scatter(good["laufzeit"], good["hoehe"], alpha=0.55, label="good", s=25)
ax4.scatter(bad["laufzeit"], bad["hoehe"], alpha=0.55, label="bad", s=25)
ax4.set_title("Dispercion: duracion vs monto del credito")
ax4.set_xlabel("Duracion del credito (meses)")
ax4.set_ylabel("Monto del credito (DM)")
ax4.legend(title="credit_risk")
fig4.tight_layout()
fig4.savefig(os.path.join(BASE, "fig4_dispersion_monto_plazo.png"), dpi=150)
plt.close(fig4)

fig5, ax5 = plt.subplots(figsize=(6.5, 5.5))
corr = df[["laufzeit", "hoehe", "alter", "kredit"]].corr()
im = ax5.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax5.set_xticks(range(len(corr)), corr.columns)
ax5.set_yticks(range(len(corr)), corr.columns)
for i in range(len(corr)):
    for j in range(len(corr)):
        ax5.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                 color="white" if abs(corr.iloc[i, j]) > 0.5 else "black", fontsize=9)
ax5.set_title("Matriz de correlacion (variables numericas + objetivo)")
fig5.colorbar(im, ax=ax5, fraction=0.046)
fig5.tight_layout()
fig5.savefig(os.path.join(BASE, "fig5_correlacion.png"), dpi=150)
plt.close(fig5)

# ---------------------------------------------------------------- estadisticos
print("=== SECCION 2 ===")
print("shape:", df.shape)
print("columns:", list(df.columns))
print("dtypes:")
print(df.dtypes.to_string())

print("\n=== SECCION 5.1 nulos ===")
resumen_nulos = df.isnull().sum()
print("total:", int(resumen_nulos.sum()))
print(resumen_nulos[resumen_nulos > 0].to_string() if resumen_nulos.sum() else "ninguno")

print("\n=== SECCION 5.2 duplicados ===")
print("exactos:", int(df.duplicated().sum()))

print("\n=== SECCION 5.3 consistencia de codigos ===")
validos = {
    "laufkont": range(1, 5), "moral": range(0, 5), "verw": range(0, 11),
    "sparkont": range(1, 6), "beszeit": range(1, 6), "rate": range(1, 5),
    "famges": range(1, 5), "buerge": range(1, 4), "wohnzeit": range(1, 5),
    "verm": range(1, 5), "weitkred": range(1, 4), "wohn": range(1, 4),
    "bishkred": range(1, 5), "beruf": range(1, 5), "pers": range(1, 3),
    "telef": range(1, 3), "gastarb": range(1, 3), "kredit": range(0, 2),
}
for col, codigos in validos.items():
    if len(bad := df.loc[~df[col].isin(codigos), col]):
        print("FUERA_DE_CODIGO", col, sorted(bad.unique()))
for col, codigos in validos.items():
    faltantes = sorted(set(codigos) - set(df[col].unique()))
    if faltantes:
        print("CATALOGO_SIN_DATOS", col, faltantes)
rangos_logicos = {"laufzeit": (1, 120), "hoehe": (0, None), "alter": (18, 100)}
for col, (lo, hi) in rangos_logicos.items():
    out = df[(df[col] < lo) | (hi is not None and df[col] > hi)]
    print("FUERA_DE_RANGO_NEGOCIO", col, len(out))

print("\n=== SECCION 6 estadisticas ===")
for col in ["laufzeit", "hoehe", "alter"]:
    s = df[col]
    print(f"{col}: media={s.mean():.2f} mediana={s.median():.2f} min={s.min()} "
          f"max={s.max()} std={s.std():.2f} Q1={s.quantile(.25)} Q3={s.quantile(.75)}")

print("\n=== SECCION 7 outliers IQR ===")
for col in ["laufzeit", "hoehe", "alter"]:
    s = df[col]
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (s < lo) | (s > hi)
    print(f"{col}: lim_inf={lo:.1f} lim_sup={hi:.1f} n_outliers={mask.sum()} "
          f"({mask.mean()*100:.1f}%) max={s.max()}")
print("outliers laufzeit valores tipicos:", sorted(df.loc[df['laufzeit'] > 42, 'laufzeit'].unique()))

print("\n=== SECCION 8 apoyo ===")
print("por clase:")
print(df.groupby("kredit")[["hoehe", "laufzeit", "alter"]].agg(["mean", "median"]).round(2).to_string())
print("correlacion:")
print(df[["laufzeit", "hoehe", "alter", "kredit"]].corr().round(3).to_string())
print("\nFiguras guardadas en", os.path.abspath(BASE))
