"""
Clustering y PCA — South German Credit (Unidad IV / Fase 4)
Segmentación no supervisada de clientes con K-means y reducción con PCA.

Diseño:
  - Features sin el objetivo: se excluyen `kredit`, `kredit_cat` (el clustering
    NO debe verse la respuesta) y `cuota_aprox_mensual` (duplicaría hoehe/laufzeit).
  - Matriz: 3 numéricas estandarizadas + 17 categóricas one-hot (~60 columnas).
  - PCA completo: varianza explicada, componentes para 80/90 %, loadings de PC1/PC2.
  - K-means con k=2..8: selección por codo (inercia) + silhouette.
  - Perfil de cada clúster: medias de numéricas, % bad (validación post-hoc)
    y categorías distintivas.

Uso:
    py src/models/clustering_pca.py
Salidas:
    modelos/clustering/kmeans_credit.pkl + metricas.json
    docs/modelos/figuras/pca_varianza.png, pca_clusters.png,
                        kmeans_seleccion_k.png, clu_perfil_bad.png
"""
import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CSV_PATH = os.path.join('data', 'processed', 'south_german_credit_processed.csv')
OUT_DIR = os.path.join('modelos', 'clustering')
FIG_DIR = os.path.join('docs', 'modelos', 'figuras')

NUM_FEATS = ['laufzeit', 'hoehe', 'alter']
CAT_FEATS = ['laufkont_cat', 'moral_cat', 'verw_cat', 'sparkont_cat',
             'beszeit_cat', 'rate_cat', 'famges_cat', 'buerge_cat',
             'wohnzeit_cat', 'verm_cat', 'weitkred_cat', 'wohn_cat',
             'bishkred_cat', 'beruf_cat', 'pers_cat', 'telef_cat',
             'gastarb_cat']
EXCLUIDAS = ['kredit', 'kredit_cat', 'cuota_aprox_mensual']


def construir_matriz(df):
    """ColumnTransformer: numéricas estandarizadas + categóricas one-hot."""
    prep = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUM_FEATS),
            ('cat', OneHotEncoder(handle_unknown='ignore'), CAT_FEATS),
        ],
        remainder='drop',
    )
    X = prep.fit_transform(df)
    nombres = prep.get_feature_names_out()
    return X, nombres, prep


def pca_completo(X, nombres, fig_dir=FIG_DIR):
    """PCA total: varianza, componentes para 80/90 % y loadings de PC1/PC2."""
    pca = PCA(random_state=42).fit(X)
    var = pca.explained_variance_ratio_
    acum = np.cumsum(var)
    n80 = int(np.argmax(acum >= 0.80) + 1)
    n90 = int(np.argmax(acum >= 0.90) + 1)

    # figura: scree + acumulada
    os.makedirs(fig_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    eje = np.arange(1, len(var) + 1)
    ax.bar(eje, var * 100, color='#4C72B0', alpha=0.8, label='varianza explicada')
    ax.plot(eje, acum * 100, color='#C44E52', marker='o', ms=3,
            label='acumulada')
    ax.axhline(80, ls='--', color='gray', lw=1)
    ax.axhline(90, ls='--', color='gray', lw=1)
    ax.annotate(f'80 % → {n80} CP', xy=(n80, 80), fontsize=9,
                xytext=(n80 + 3, 70), arrowprops=dict(arrowstyle='->'))
    ax.annotate(f'90 % → {n90} CP', xy=(n90, 90), fontsize=9,
                xytext=(n90 + 3, 60), arrowprops=dict(arrowstyle='->'))
    ax.set_xlabel('Componente principal')
    ax.set_ylabel('Varianza (%)')
    ax.set_title('PCA — varianza explicada por componente')
    ax.legend()
    fig.tight_layout()
    ruta_scree = os.path.join(fig_dir, 'pca_varianza.png')
    fig.savefig(ruta_scree, dpi=150)
    plt.close(fig)

    # loadings de PC1 y PC2 (top |peso|)
    comps = pd.DataFrame(pca.components_[:2].T, index=nombres,
                         columns=['PC1', 'PC2'])
    top = (comps.assign(abs1=comps['PC1'].abs(), abs2=comps['PC2'].abs())
           .sort_values('abs1', ascending=False)
           .drop(columns=['abs1', 'abs2']))
    return pca, var, acum, n80, n90, top, ruta_scree


def proyectar_2d(pca, X, etiquetas_clusters, ruta_out):
    """Dispersión PC1-PC2 coloreada por clúster."""
    Z = pca.transform(X)[:, :2]
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    for k in np.unique(etiquetas_clusters):
        m = etiquetas_clusters == k
        ax.scatter(Z[m, 0], Z[m, 1], s=22, alpha=0.65, label=f'clúster {k}')
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_title('Clústeres K-means en el plano PCA (PC1 vs PC2)')
    ax.legend()
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=150)
    plt.close(fig)
    return ruta_out


def seleccionar_k(X, k_min=2, k_max=8, semilla=42):
    """Inercia (codo) y silhouette para k en [k_min, k_max]."""
    filas = []
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=semilla)
        labels = km.fit_predict(X)
        filas.append({'k': k, 'inercia': km.inertia_,
                      'silhouette': silhouette_score(X, labels)})
    return pd.DataFrame(filas)


def graficar_seleccion_k(tabla, ruta_out):
    fig, ax1 = plt.subplots(figsize=(7.2, 4.6))
    ax1.plot(tabla['k'], tabla['inercia'], marker='o', color='#4C72B0',
             label='inercia (codo)')
    ax1.set_xlabel('k (número de clústeres)')
    ax1.set_ylabel('Inercia', color='#4C72B0')
    ax2 = ax1.twinx()
    ax2.plot(tabla['k'], tabla['silhouette'], marker='s', color='#C44E52',
             label='silhouette')
    ax2.set_ylabel('Silhouette', color='#C44E52')
    mejor_k = int(tabla.loc[tabla['silhouette'].idxmax(), 'k'])
    ax2.axvline(mejor_k, ls='--', color='gray', lw=1)
    ax2.annotate(f'mejor k = {mejor_k}', xy=(mejor_k, tabla['silhouette'].max()),
                 xytext=(mejor_k + 0.5, tabla['silhouette'].max() * 0.97),
                 fontsize=9)
    ax1.set_title('Selección de k: codo (inercia) y silhouette')
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=150)
    plt.close(fig)
    return mejor_k, ruta_out


def perfil_clusters(df, X, nombres, labels):
    """Resumen por clúster: tamaño, medias, % bad y categorías distintivas."""
    d = df.assign(cluster=labels)
    base = d.groupby('cluster').agg(
        tamaño=('kredit', 'size'),
        pct_bad=('kredit', lambda s: round(100 * (1 - s.mean()), 1)),
        plazo_medio=('laufzeit', 'mean'),
        monto_medio=('hoehe', 'mean'),
        edad_media=('alter', 'mean'),
    )
    # categorías distintivas: dummies one-hot con mayor desvío vs. global
    Xd = X.toarray() if hasattr(X, 'toarray') else np.asarray(X)
    dummies = pd.DataFrame(Xd, columns=nombres)
    cols_cat = [c for c in dummies.columns if c.startswith('cat__')]
    global_mean = dummies[cols_cat].mean()
    desvios = {}
    for k in sorted(d['cluster'].unique()):
        medias = dummies.loc[d['cluster'] == k, cols_cat].mean()
        desvios[k] = (medias - global_mean).sort_values()
    return base.round(1), desvios


def graficar_bad_por_cluster(base, ruta_out):
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    base['pct_bad'].plot(kind='bar', ax=ax, color='#C44E52', alpha=0.85)
    ax.axhline(30, ls='--', color='gray', lw=1)
    ax.annotate('30 % base', xy=(0.02, 30.8), fontsize=9, color='gray',
                xycoords='axes fraction')
    ax.set_xlabel('Clúster')
    ax.set_ylabel('% bad')
    ax.set_title('Riesgo real (bad) por clúster — validación post-hoc')
    ax.set_xticklabels(base.index, rotation=0)
    fig.tight_layout()
    fig.savefig(ruta_out, dpi=150)
    plt.close(fig)
    return ruta_out


def main(semilla=42):
    df = pd.read_csv(CSV_PATH)
    print('dataset:', df.shape)

    X, nombres, prep = construir_matriz(df)
    print('matriz de clustering:', X.shape)

    pca, var, acum, n80, n90, top_load, ruta_scree = pca_completo(X, nombres)
    print(f'PCA: {len(var)} componentes | 80% var = {n80} CP | 90% = {n90} CP')
    print('top loadings PC1:')
    print(top_load.head(6).round(3).to_string())

    tabla_k = seleccionar_k(X, 2, 8, semilla)
    print('\nselección de k:')
    print(tabla_k.round(3).to_string(index=False))
    mejor_k, ruta_sel = graficar_seleccion_k(
        tabla_k, os.path.join(FIG_DIR, 'kmeans_seleccion_k.png'))
    print('mejor k por silhouette:', mejor_k)

    km = KMeans(n_clusters=mejor_k, n_init=10, random_state=semilla)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)

    ruta_scatter = proyectar_2d(
        pca, X, labels, os.path.join(FIG_DIR, 'pca_clusters.png'))

    base, desvios = perfil_clusters(df, X, nombres, labels)
    print('\nperfil de clústeres:')
    print(base.to_string())
    ruta_bad = graficar_bad_por_cluster(
        base, os.path.join(FIG_DIR, 'clu_perfil_bad.png'))

    top_distintivos = {int(k): {'mas_presentes': [(v.split('__')[-1], round(float(x), 3))
                                                  for v, x in desvios[k].sort_values(ascending=False).head(5).items()],
                                'mas_ausentes': [(v.split('__')[-1], round(float(x), 3))
                                                 for v, x in desvios[k].sort_values().head(5).items()]}
                       for k in desvios}

    os.makedirs(OUT_DIR, exist_ok=True)
    ruta_modelo = os.path.join(OUT_DIR, 'kmeans_credit.pkl')
    joblib.dump({'preprocesador': prep, 'kmeans': km, 'pca': pca}, ruta_modelo)

    salida = {
        'fecha': pd.Timestamp.now().isoformat(timespec='seconds'),
        'dataset': CSV_PATH,
        'matriz_shape': list(X.shape),
        'excluidas': EXCLUIDAS,
        'pca': {
            'n_componentes': int(len(var)),
            'var_primeras5': [round(float(v), 4) for v in var[:5]],
            'cp_para_80pct': n80,
            'cp_para_90pct': n90,
            'top_loadings_pc1': top_load.head(8).round(3).to_dict(orient='index'),
        },
        'seleccion_k': tabla_k.round(3).to_dict(orient='records'),
        'mejor_k': mejor_k,
        'silhouette': round(float(sil), 3),
        'inercia': round(float(km.inertia_), 1),
        'perfil_clusters': base.reset_index().to_dict(orient='records'),
        'categorias_distintivas': top_distintivos,
        'modelo_guardado': ruta_modelo,
        'figuras': [ruta_scree, ruta_sel, ruta_scatter, ruta_bad],
    }
    ruta_json = os.path.join(OUT_DIR, 'metricas.json')
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print('\nmetricas guardadas:', ruta_json)
    print('figuras:', salida['figuras'])
    return salida


if __name__ == '__main__':
    main()
