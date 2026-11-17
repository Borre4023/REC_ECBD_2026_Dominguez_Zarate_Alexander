"""
Generador del dashboard HTML estático — South German Credit (Fase 5)
Lee KPIs y consultas Q1–Q5 del Data Mart SQLite, incrusta figuras
(matplotlib → PNG base64) y renderiza src/dashboard/plantilla.html.

Salida autocontenida: se abre en cualquier navegador sin servidor ni internet.

Uso:
    py src/dashboard/generar_dashboard.py
Salida:
    dashboard/index.html
"""
import base64
import json
import os
import sqlite3
from datetime import date

import pandas as pd
from jinja2 import Template

# raíz del repo: src/dashboard/generar_dashboard.py → 3 niveles arriba
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'dw_south_german_credit.db')
FIG_DIR = os.path.join(BASE_DIR, 'docs', 'modelos', 'figuras')
PLANTILLA = os.path.join(BASE_DIR, 'src', 'dashboard', 'plantilla.html')
SALIDA = os.path.join(BASE_DIR, 'dashboard', 'index.html')

# consultas sobre el modelo estrella / vista dm_riesgo_crediticio
SQL_KPIS = """
SELECT COUNT(*)                                   AS n_creditos,
       ROUND(100.0 * SUM(riesgo_credito = 0) / COUNT(*), 1) AS pct_bad,
       SUM(monto_dm)                              AS monto_total,
       ROUND(AVG(monto_dm), 0)                    AS monto_medio,
       ROUND(AVG(duracion_meses), 1)              AS plazo_medio
FROM fact_credito"""

SQL_Q1 = """
SELECT h.historial_crediticio AS clave, COUNT(*) AS creditos,
       SUM(f.riesgo_credito = 0) AS bad,
       ROUND(100.0 * SUM(f.riesgo_credito = 0) / COUNT(*), 1) AS pct_bad
FROM fact_credito f JOIN dim_hist_credito h ON h.sk_hist = f.sk_hist
GROUP BY clave ORDER BY pct_bad DESC"""

SQL_Q3 = """
SELECT cu.estado_cuenta || ' + ahorros ' || cu.ahorros AS clave,
       COUNT(*) AS creditos,
       ROUND(100.0 * SUM(f.riesgo_credito = 0) / COUNT(*), 1) AS pct_bad
FROM fact_credito f JOIN dim_cuenta cu ON cu.sk_cuenta = f.sk_cuenta
GROUP BY clave HAVING COUNT(*) >= 10 ORDER BY pct_bad DESC"""

SQL_Q5 = """
SELECT CASE WHEN monto_dm < 1500  THEN 'a. < 1500 DM'
            WHEN monto_dm < 4000  THEN 'b. 1500-3999 DM'
            WHEN monto_dm < 8000  THEN 'c. 4000-7999 DM'
            ELSE 'd. >= 8000 DM' END AS clave,
       COUNT(*) AS creditos, ROUND(AVG(monto_dm), 0) AS monto_medio,
       ROUND(100.0 * SUM(riesgo_credito = 0) / COUNT(*), 1) AS pct_bad
FROM fact_credito GROUP BY clave ORDER BY clave"""

SQL_Q2 = """
SELECT p.proposito AS clave, COUNT(*) AS creditos,
       ROUND(AVG(f.monto_dm), 0) AS monto_medio,
       ROUND(AVG(f.monto_dm * 1.0 / f.duracion_meses), 1) AS cuota_media
FROM fact_credito f JOIN dim_proposito p ON p.sk_proposito = f.sk_proposito
GROUP BY clave ORDER BY monto_medio DESC LIMIT 6"""

SQL_Q4 = """
SELECT sk_credito, monto_dm, duracion_meses, cuota_aprox_mensual AS cuota,
       historial_crediticio AS historial, proposito, riesgo_credito_cat AS resultado
FROM dm_riesgo_crediticio ORDER BY cuota_aprox_mensual DESC LIMIT 10"""


def consultar(sql):
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, con)
    con.close()
    return df


def df_a_html(df, formateos=None):
    """Tabla HTML con alineación numérica y clase según contenido."""
    d = df.copy()
    if formateos:
        for col, fmt in formateos.items():
            d[col] = d[col].map(lambda v: fmt(v))
    clases = {c: ('num' if pd.api.types.is_numeric_dtype(df[c]) else '')
              for c in d.columns}
    th = ''.join(f'<th class="{clases[c]}">{c}</th>' for c in d.columns)
    filas = []
    for _, r in d.iterrows():
        tds = ''.join(f'<td class="{clases[c]}">{r[c]}</td>' for c in d.columns)
        filas.append(f'<tr>{tds}</tr>')
    return (f'<table><thead><tr>{th}</tr></thead><tbody>'
            + ''.join(filas) + '</tbody></table>')


def figura_base64(nombre):
    ruta = os.path.join(FIG_DIR, nombre)
    with open(ruta, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')


def main():
    fecha = date.today().isoformat()

    # ---- KPIs ----
    k = consultar(SQL_KPIS).iloc[0]
    cuota_media = consultar(
        'SELECT ROUND(AVG(monto_dm * 1.0 / duracion_meses), 1) AS c '
        'FROM fact_credito').iloc[0]['c']
    kpis = {
        'n_creditos': f"{int(k['n_creditos']):,}".replace(',', ' '),
        'pct_bad': k['pct_bad'],
        'monto_total': f"{int(k['monto_total']):,}".replace(',', ' '),
        'monto_medio': f"{int(k['monto_medio']):,}".replace(',', ' '),
        'plazo_medio': k['plazo_medio'],
        'cuota_media': cuota_media,
    }

    # ---- Q1 historial ----
    q1df = consultar(SQL_Q1)
    tabla_q1 = df_a_html(q1df, {'pct_bad': lambda v: f'<span class="bad">{v}%</span>'})
    q1 = {'peor': q1df.iloc[0], 'mejor': q1df.iloc[-1]}

    # ---- Q3 cuenta+ahorros (≥10 créditos, todas las combinaciones) ----
    q3df = consultar(SQL_Q3)
    tabla_q3 = df_a_html(q3df, {'pct_bad': lambda v: f'<span class="bad">{v}%</span>'})
    q3_peor = q3df.iloc[0]
    clave_mejor = 'ge200_or_salary + ahorros ge1000'
    q3_mejor = q3df.loc[q3df['clave'] == clave_mejor].iloc[0]
    q3 = {'peor': q3_peor, 'mejor': q3_mejor,
          'razon': round(q3_peor['pct_bad'] / q3_mejor['pct_bad'], 1)}

    # ---- Q5 monto ----
    q5df = consultar(SQL_Q5)
    tabla_q5 = df_a_html(q5df, {'monto_medio': lambda v: f"{int(v):,}".replace(',', ' '),
                                'pct_bad': lambda v: f'<span class="bad">{v}%</span>'})
    minimo = q5df.loc[q5df['pct_bad'].idxmin()]
    maximo = q5df.loc[q5df['pct_bad'].idxmax()]
    q5 = {'minimo': minimo, 'maximo': maximo}

    # ---- Q2 propósito ----
    q2df = consultar(SQL_Q2)
    tabla_q2 = df_a_html(q2df, {'monto_medio': lambda v: f"{int(v):,}".replace(',', ' '),
                                'cuota_media': lambda v: f'{v} DM'})

    # ---- Q4 top exposición ----
    q4df = consultar(SQL_Q4)
    tabla_q4 = df_a_html(q4df, {
        'monto_dm': lambda v: f"{int(v):,}".replace(',', ' '),
        'cuota': lambda v: f'{v} DM',
        'resultado': lambda v: (f'<span class="bad">{v}</span>' if v == 'bad'
                                else f'<span class="good">{v}</span>')})
    q4 = {'pct_bad_top': int(100 * (q4df['resultado'] == 'bad').sum() / len(q4df))}

    # ---- Modelos (metricas.json reales) ----
    with open(os.path.join(BASE_DIR, 'modelos', 'clasificacion', 'metricas.json'),
              encoding='utf-8') as f:
        m_cla = json.load(f)
    with open(os.path.join(BASE_DIR, 'modelos', 'regresion', 'metricas.json'),
              encoding='utf-8') as f:
        m_reg = json.load(f)
    cm = m_cla['matriz_confusion_test']  # [[TP,FN],[FP,TN]]
    modelos = {
        'auc': round(m_cla['metricas_test']['roc_auc_test'], 3),
        'recall_bad': round(100 * cm[0][0] / (cm[0][0] + cm[0][1])),
        'fp': cm[1][0],
        'r2': round(m_reg['metricas_test']['r2_test'], 3),
    }

    # ---- Clustering (metricas.json real) ----
    with open(os.path.join(BASE_DIR, 'modelos', 'clustering', 'metricas.json'),
              encoding='utf-8') as f:
        m_clu = json.load(f)
    clus = {c['cluster']: c for c in m_clu['perfil_clusters']}
    tabla_clusters = df_a_html(pd.DataFrame([
        {'segmento': 'exposición alta' if c == 0 else 'exposición baja',
         'clientes': int(v['tamaño']),
         'monto medio (DM)': int(v['monto_medio']),
         'plazo (meses)': v['plazo_medio'],
         '% bad real': v['pct_bad']}
        for c, v in clus.items()]),
        {'monto medio (DM)': lambda v: f"{int(v):,}".replace(',', ' '),
         '% bad real': lambda v: f'<span class="bad">{v}%</span>'})
    clu0 = {'monto': f"{int(clus[0]['monto_medio']):,}".replace(',', ' '),
            'pct_bad': clus[0]['pct_bad']}
    clu1 = {'monto': f"{int(clus[1]['monto_medio']):,}".replace(',', ' '),
            'pct_bad': clus[1]['pct_bad']}

    # ---- Figuras base64 ----
    fig_roc = figura_base64('roc_curvas.png')
    fig_matriz = figura_base64('matriz_confusion.png')
    fig_clusters = figura_base64('pca_clusters.png')
    fig_perfil_bad = figura_base64('clu_perfil_bad.png')

    with open(PLANTILLA, encoding='utf-8') as f:
        html = Template(f.read()).render(
            fecha=fecha, kpis=kpis, tabla_q1=tabla_q1, q1=q1,
            tabla_q3=tabla_q3, q3=q3, tabla_q5=tabla_q5, q5=q5,
            tabla_q2=tabla_q2, tabla_q4=tabla_q4, q4=q4,
            modelos=modelos, tabla_clusters=tabla_clusters,
            clu0=clu0, clu1=clu1,
            fig_roc=fig_roc, fig_matriz=fig_matriz,
            fig_clusters=fig_clusters, fig_perfil_bad=fig_perfil_bad)

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        f.write(html)
    print('dashboard generado:', SALIDA, f'({os.path.getsize(SALIDA):,} bytes)')
    return SALIDA


if __name__ == '__main__':
    main()
