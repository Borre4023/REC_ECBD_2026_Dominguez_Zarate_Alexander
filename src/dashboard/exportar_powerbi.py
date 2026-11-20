"""
Exportador de datos para Power BI — South German Credit (Unidad V, alternativa)
Genera CSV listos para importar en Power BI Desktop desde el Data Mart SQLite
y los artefactos de los modelos. Mismas 4 páginas que el dashboard HTML.

Uso:
    py src/dashboard/exportar_powerbi.py
Salidas (powerbi/datos/):
    dm_riesgo_crediticio.csv   1000 creditos x 23 columnas (vista plana)
    segmentos.csv              2 clusters con su perfil
    pca_coordenadas.csv        PC1/PC2 + cluster por credito
    pca_varianza.csv           70 CP: varianza explicada y acumulada
    seleccion_k.csv            k=2..8: inercia y silhouette
    metricas_modelos.csv       metrica/valor por modelo (largo)
    matriz_confusion.csv       real x pred (bad/good)

Formato: UTF-8 con BOM, separador ';', decimales con punto (estandar es-MX).
"""
import json
import os
import sqlite3

import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'dw_south_german_credit.db')
CSV_PROCESADO = os.path.join(BASE_DIR, 'data', 'processed',
                             'south_german_credit_processed.csv')
PKL_CLUSTERING = os.path.join(BASE_DIR, 'modelos', 'clustering', 'kmeans_credit.pkl')
JSON_CLUSTERING = os.path.join(BASE_DIR, 'modelos', 'clustering', 'metricas.json')
JSON_CLASIFICACION = os.path.join(BASE_DIR, 'modelos', 'clasificacion', 'metricas.json')
JSON_REGRESION = os.path.join(BASE_DIR, 'modelos', 'regresion', 'metricas.json')
OUT_DIR = os.path.join(BASE_DIR, 'powerbi', 'datos')

NUM_FEATS = ['laufzeit', 'hoehe', 'alter']
CAT_FEATS = ['laufkont_cat', 'moral_cat', 'verw_cat', 'sparkont_cat',
             'beszeit_cat', 'rate_cat', 'famges_cat', 'buerge_cat',
             'wohnzeit_cat', 'verm_cat', 'weitkred_cat', 'wohn_cat',
             'bishkred_cat', 'beruf_cat', 'pers_cat', 'telef_cat',
             'gastarb_cat']


def guardar_csv(df, nombre):
    ruta = os.path.join(OUT_DIR, nombre)
    df.to_csv(ruta, sep=';', index=False, encoding='utf-8-sig', decimal='.')
    print(f'{nombre}: {len(df)} filas x {len(df.columns)} columnas')
    return ruta


def exportar_vista():
    con = sqlite3.connect(DB_PATH)
    vista = pd.read_sql_query('SELECT * FROM dm_riesgo_crediticio '
                              'ORDER BY sk_credito', con)
    con.close()
    guardar_csv(vista, 'dm_riesgo_crediticio.csv')
    return vista


def exportar_segmentos(m_clu):
    # el segmento de exposición alta es el de mayor monto medio (no depende de la etiqueta)
    alta = max(m_clu['perfil_clusters'], key=lambda c: c['monto_medio'])['cluster']
    filas = [{'cluster': c['cluster'],
              'segmento': 'exposicion_alta' if c['cluster'] == alta else 'exposicion_baja',
              'clientes': int(c['tamaño']),
              'monto_medio_dm': round(float(c['monto_medio']), 1),
              'plazo_medio_meses': float(c['plazo_medio']),
              'edad_media': float(c['edad_media']),
              'pct_bad': float(c['pct_bad'])}
             for c in sorted(m_clu['perfil_clusters'], key=lambda x: x['cluster'])]
    guardar_csv(pd.DataFrame(filas), 'segmentos.csv')


def exportar_pca(vista):
    """PC1/PC2 y cluster recalculados con el pkl (mismo pipeline del notebook 05)."""
    artefacto = joblib.load(PKL_CLUSTERING)
    df = pd.read_csv(CSV_PROCESADO)
    X = artefacto['preprocesador'].transform(df[NUM_FEATS + CAT_FEATS])
    etiquetas = artefacto['kmeans'].predict(X)
    Z = artefacto['pca'].transform(X)[:, :2]
    var = artefacto['pca'].explained_variance_ratio_
    acum = np.cumsum(var)

    # la vista y la matriz de clustering están en el mismo orden de créditos
    if len(vista) != len(df):
        raise ValueError('La vista y el dataset procesado no tienen el mismo tamaño')
    coords = pd.DataFrame({
        'sk_credito': vista['sk_credito'].astype(int),
        'pc1': np.round(Z[:, 0], 4),
        'pc2': np.round(Z[:, 1], 4),
        'cluster': etiquetas.astype(int),
        'riesgo_credito': vista['riesgo_credito'].astype(int),
        'riesgo_credito_cat': vista['riesgo_credito_cat'],
    })
    guardar_csv(coords, 'pca_coordenadas.csv')

    varianza = pd.DataFrame({
        'componente': np.arange(1, len(var) + 1),
        'var_explicada_pct': np.round(var * 100, 3),
        'acumulada_pct': np.round(acum * 100, 3),
    })
    guardar_csv(varianza, 'pca_varianza.csv')


def exportar_seleccion_k(m_clu):
    filas = [{'k': int(f['k']),
              'inercia': round(float(f['inercia']), 2),
              'silhouette': round(float(f['silhouette']), 4)}
             for f in m_clu['seleccion_k']]
    guardar_csv(pd.DataFrame(filas), 'seleccion_k.csv')


def exportar_metricas(m_cla, m_reg):
    cla = m_cla['metricas_test']
    reg = m_reg['metricas_test']
    cv_cla = {f['modelo']: f for f in m_cla['comparacion_cv']}
    cv_reg = {f['modelo']: f for f in m_reg['comparacion_cv']}
    mejor_cla = cv_cla[m_cla['mejor_modelo']]
    mejor_reg = cv_reg[m_reg['mejor_modelo']]

    filas = [
        # clasificación (clase positiva = bad)
        ('clasificacion', 'logistica_bal_C01', 'roc_auc', cla['roc_auc_test'], 'test'),
        ('clasificacion', 'logistica_bal_C01', 'roc_auc', mejor_cla['roc_auc_cv'], 'cv_5fold'),
        ('clasificacion', 'logistica_bal_C01', 'accuracy', cla['accuracy_test'], 'test'),
        ('clasificacion', 'logistica_bal_C01', 'precision_bad', cla['precision_bad'], 'test'),
        ('clasificacion', 'logistica_bal_C01', 'recall_bad', cla['recall_bad'], 'test'),
        ('clasificacion', 'logistica_bal_C01', 'f1_bad', cla['f1_bad'], 'test'),
        ('clasificacion', 'logistica_bal_C01', 'f1_bad', mejor_cla['f1_bad_cv'], 'cv_5fold'),
        # regresión
        ('regresion', 'ridge_cv', 'r2', reg['r2_test'], 'test'),
        ('regresion', 'ridge_cv', 'r2', mejor_reg['r2_cv'], 'cv_5fold'),
        ('regresion', 'ridge_cv', 'rmse_dm', reg['rmse_test'], 'test'),
        ('regresion', 'ridge_cv', 'rmse_dm', mejor_reg['rmse_cv'], 'cv_5fold'),
        ('regresion', 'ridge_cv', 'mae_dm', reg['mae_test'], 'test'),
        ('regresion', 'ridge_cv', 'mae_dm', mejor_reg['mae_cv'], 'cv_5fold'),
    ]
    df = pd.DataFrame(filas, columns=['problema', 'modelo', 'metrica', 'valor', 'conjunto'])
    df['valor'] = df['valor'].astype(float).round(4)
    guardar_csv(df, 'metricas_modelos.csv')


def exportar_matriz(m_cla):
    (tp, fn), (fp, tn) = m_cla['matriz_confusion_test']
    filas = [
        ('real bad', 'pred bad', 'TP', int(tp)),
        ('real bad', 'pred good', 'FN', int(fn)),
        ('real good', 'pred bad', 'FP', int(fp)),
        ('real good', 'pred good', 'TN', int(tn)),
    ]
    df = pd.DataFrame(filas, columns=['real', 'prediccion', 'tipo', 'creditos'])
    guardar_csv(df, 'matriz_confusion.csv')


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSON_CLUSTERING, encoding='utf-8') as f:
        m_clu = json.load(f)
    with open(JSON_CLASIFICACION, encoding='utf-8') as f:
        m_cla = json.load(f)
    with open(JSON_REGRESION, encoding='utf-8') as f:
        m_reg = json.load(f)

    vista = exportar_vista()
    exportar_segmentos(m_clu)
    exportar_pca(vista)
    exportar_seleccion_k(m_clu)
    exportar_metricas(m_cla, m_reg)
    exportar_matriz(m_cla)
    print('CSV para Power BI en:', OUT_DIR)


if __name__ == '__main__':
    main()
