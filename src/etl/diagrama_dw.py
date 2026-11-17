"""
Diagrama del esquema estrella del Data Mart — South German Credit (Fase 6)
Genera un PNG con matplotlib: 8 dimensiones -> fact_credito -> vista
dm_riesgo_crediticio, con conteos de filas reales leídos de la BD.

Uso:
    py src/etl/diagrama_dw.py
Salida:
    docs/analisis/figuras/diagrama_dw.png
"""
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'dw_south_german_credit.db')
SALIDA = os.path.join(BASE_DIR, 'docs', 'analisis', 'figuras', 'diagrama_dw.png')

DIMS = {
    'dim_cliente':      'atributos: edad,\nestado civil/sexo,\nteléfono, empleo…',
    'dim_cuenta':       'estado de cuenta,\nahorros',
    'dim_hist_credito': 'historial crediticio',
    'dim_proposito':    'propósito',
    'dim_bien':         'bien más valioso',
    'dim_planes':       'otros planes\nde cuotas',
    'dim_deudor':       'otros deudores /\naval',
    'dim_vivienda':     'tipo de vivienda',
}
# posiciones (x, y): fila superior e inferior
POS = {
    'dim_cliente':      (1.25, 6.9),
    'dim_cuenta':       (3.75, 6.9),
    'dim_hist_credito': (6.25, 6.9),
    'dim_proposito':    (8.75, 6.9),
    'dim_planes':       (1.25, 1.1),
    'dim_deudor':       (3.75, 1.1),
    'dim_bien':         (6.25, 1.1),
    'dim_vivienda':     (8.75, 1.1),
}
FK_LABEL = {
    'dim_cliente': 'sk_cliente', 'dim_cuenta': 'sk_cuenta',
    'dim_hist_credito': 'sk_hist', 'dim_proposito': 'sk_proposito',
    'dim_bien': 'sk_bien', 'dim_planes': 'sk_plan',
    'dim_deudor': 'sk_deudor', 'dim_vivienda': 'sk_vivienda',
}
FACT_POS = (5.0, 4.0)
FACT_W, FACT_H = 3.3, 1.9
VIEW_POS = (8.75, 4.0)
VIEW_W, VIEW_H = 2.3, 1.5
DIM_W, DIM_H = 1.95, 1.30


def contar(con, tabla):
    return con.execute(f'SELECT COUNT(*) FROM {tabla}').fetchone()[0]


def caja(ax, x, y, w, h, titulo, cuerpo, fc, ec, titulo_fs=10, cuerpo_fs=7.6):
    b = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                       boxstyle='round,pad=0.06', fc=fc, ec=ec, lw=1.6, zorder=3)
    ax.add_patch(b)
    ax.text(x, y + h / 2 - 0.26, titulo, ha='center', va='center',
            fontsize=titulo_fs, fontweight='bold', color='white', zorder=4)
    ax.text(x, y - 0.22, cuerpo, ha='center', va='center', fontsize=cuerpo_fs,
            color='#16202b', zorder=4)


def main():
    con = sqlite3.connect(DB_PATH)
    n_fact = contar(con, 'fact_credito')
    n_view = contar(con, 'dm_riesgo_crediticio')

    fig, ax = plt.subplots(figsize=(13.8, 9.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.6)
    ax.axis('off')
    ax.set_title('Data Mart "riesgo crediticio" — esquema estrella (SQLite) · '
                 'Proyecto South German Credit · UTTT',
                 fontsize=13, fontweight='bold', color='#1d3f5c', pad=22)

    # --- flechas dimension -> hecho (debajo de las cajas) ---
    for nombre, (x, y) in POS.items():
        arr = FancyArrowPatch((x, y), FACT_POS, arrowstyle='-|>',
                              mutation_scale=12, lw=1.1, color='#8aa4b8',
                              connectionstyle='arc3,rad=0.04', zorder=1)
        ax.add_patch(arr)

    # --- flecha hecho -> vista ---
    ax.add_patch(FancyArrowPatch((FACT_POS[0] + FACT_W / 2, FACT_POS[1]),
                                 (VIEW_POS[0] - VIEW_W / 2, VIEW_POS[1]),
                                 arrowstyle='-|>', mutation_scale=15, lw=1.6,
                                 color='#1e7a52', zorder=1))
    ax.text((FACT_POS[0] + VIEW_POS[0]) / 2, FACT_POS[1] + 0.22,
            'SELECT + JOINs', fontsize=8, color='#155a3c', style='italic',
            ha='center', zorder=4)

    # --- cajas: dimensiones ---
    for nombre, (x, y) in POS.items():
        n = contar(con, nombre)
        lineas = DIMS[nombre].split('\n')
        lineas[0] = f'{n} · ' + lineas[0]
        caja(ax, x, y, DIM_W, DIM_H, nombre, '\n'.join(lineas),
             fc='#5b84a6', ec='#1d3f5c')

    # --- tabla de hechos (centro) ---
    fact_cuerpo = (f'{n_fact} filas · 1 fila por crédito\n'
                   'medidas: duracion_meses · monto_dm ·\n'
                   'tasa_cuota · tiempo_residencia ·\n'
                   'num_creditos_banco · riesgo_credito (0/1) ·\n'
                   'riesgo_credito_cat\n'
                   '8 FKs · integridad referencial verificada')
    caja(ax, FACT_POS[0], FACT_POS[1], FACT_W, FACT_H, 'fact_credito',
         fact_cuerpo, fc='#c0392b', ec='#7d2318')

    # --- vista de consumo ---
    view_cuerpo = (f'{n_view} filas · tabla plana para BI\n'
                   'desnormaliza las 8 dimensiones\n'
                   'y recalcula en SQL:\n'
                   'cuota_aprox_mensual =\n'
                   'ROUND(monto_dm / duracion_meses, 2)')
    caja(ax, VIEW_POS[0], VIEW_POS[1], VIEW_W, VIEW_H,
         'dm_riesgo_crediticio (vista)', view_cuerpo,
         fc='#2e9464', ec='#155a3c', titulo_fs=8.5, cuerpo_fs=6.8)

    # --- etiquetas FK (cerca de cada dimensión, fuera del hecho) ---
    for nombre, (x, y) in POS.items():
        t = 0.72
        lx = FACT_POS[0] + t * (x - FACT_POS[0])
        ly = FACT_POS[1] + t * (y - FACT_POS[1])
        ax.text(lx, ly, FK_LABEL[nombre], fontsize=7.2, color='#44607a',
                ha='center', va='center', style='italic', zorder=5,
                bbox=dict(fc='white', ec='none', alpha=0.8, pad=1.2))

    # --- nota de origen (esquina superior izquierda) ---
    ax.text(0.08, 8.45,
            'Origen: data/processed/dw_south_german_credit.db · DDL: sql/schema_dw_sqlite.sql '
            '(adaptado del diseño PostgreSQL sql/schema_dw.sql)\n'
            'Creador: src/etl/build_dw_sqlite.py · Consultas analíticas: sql/queries_dm.sql',
            fontsize=7.6, color='#5d6d7e', va='top', zorder=5)

    con.close()
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    fig.savefig(SALIDA, dpi=170, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('diagrama generado:', SALIDA)


if __name__ == '__main__':
    main()
