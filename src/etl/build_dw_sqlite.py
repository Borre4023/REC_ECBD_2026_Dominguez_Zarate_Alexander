"""
Creador del Data Warehouse / Data Mart en SQLite — South German Credit
Fase 2: implementa el diseno de docs/analisis/propuesta_dw_datamart.md.

Lee el dataset procesado (ETL Fase 1), carga 8 dimensiones con
desduplicacion (SCD tipo 0) y fact_credito (1000 filas), crea la vista
dm_riesgo_crediticio y valida la integridad referencial.

Uso:
    py src/etl/build_dw_sqlite.py
Salida:
    data/processed/dw_south_german_credit.db
"""
import os
import sqlite3

import pandas as pd

PROCESSED_DIR = os.path.join('data', 'processed')
CSV_PATH = os.path.join(PROCESSED_DIR, 'south_german_credit_processed.csv')
SCHEMA_PATH = os.path.join('sql', 'schema_dw_sqlite.sql')
DB_PATH = os.path.join(PROCESSED_DIR, 'dw_south_german_credit.db')

# dimension -> (columnas de la dimension en el dataset procesado)
DIMS = {
    'dim_cliente': {
        'attrs': ['alter', 'famges_cat', 'pers_cat', 'telef_cat',
                  'gastarb_cat', 'beruf_cat'],
        'cols': ['edad', 'estado_civil_sexo', 'personas_a_cargo', 'telefono',
                 'trabajador_extranjero', 'empleo_calidad'],
    },
    'dim_cuenta': {
        'attrs': ['laufkont_cat', 'sparkont_cat'],
        'cols': ['estado_cuenta', 'ahorros'],
    },
    'dim_hist_credito': {
        'attrs': ['moral_cat'],
        'cols': ['historial_crediticio'],
    },
    'dim_proposito': {
        'attrs': ['verw_cat'],
        'cols': ['proposito'],
    },
    'dim_bien': {
        'attrs': ['verm_cat'],
        'cols': ['propiedad'],
    },
    'dim_planes': {
        'attrs': ['weitkred_cat'],
        'cols': ['otros_planes_cuota'],
    },
    'dim_deudor': {
        'attrs': ['buerge_cat'],
        'cols': ['otros_deudores'],
    },
    'dim_vivienda': {
        'attrs': ['wohn_cat'],
        'cols': ['tipo_vivienda'],
    },
}

# medidas de fact_credito: columna del dataset -> columna de la tabla
FACT_MEDIDAS = {
    'laufzeit': 'duracion_meses',
    'hoehe': 'monto_dm',
    'rate_cat': 'tasa_cuota',
    'wohnzeit_cat': 'tiempo_residencia',
    'bishkred_cat': 'num_creditos_banco',
    'kredit': 'riesgo_credito',
    'kredit_cat': 'riesgo_credito_cat',
}


def crear_esquema(con):
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        con.executescript(f.read())


def cargar_dimension(con, df, tabla, cfg):
    """Carga una dimension desduplicada y devuelve el mapa (atributos)->sk."""
    attrs, cols = cfg['attrs'], cfg['cols']
    combos = df[attrs].drop_duplicates().sort_values(attrs)
    placeholders = ', '.join('?' * len(cols))
    sql = f"INSERT INTO {tabla} ({', '.join(cols)}) VALUES ({placeholders})"
    mapa = {}
    cur = con.cursor()
    for fila in combos.itertuples(index=False):
        cur.execute(sql, tuple(fila))
        mapa[tuple(fila)] = cur.lastrowid
    con.commit()
    return mapa


def cargar_hechos(con, df, mapas):
    cols_dim = [
        'sk_cliente', 'sk_cuenta', 'sk_hist', 'sk_proposito',
        'sk_bien', 'sk_plan', 'sk_deudor', 'sk_vivienda',
    ]
    tablas_dim = list(DIMS.keys())
    todas = cols_dim + list(FACT_MEDIDAS.values())
    placeholders = ', '.join('?' * len(todas))
    sql = f"INSERT INTO fact_credito ({', '.join(todas)}) VALUES ({placeholders})"
    cur = con.cursor()
    for fila in df.itertuples(index=False):
        registro = dict(zip(df.columns, fila))
        valores = []
        for tabla, cfg in DIMS.items():
            clave = tuple(registro[a] for a in cfg['attrs'])
            valores.append(mapas[tabla][clave])
        for origen in FACT_MEDIDAS:
            valores.append(registro[origen])
        cur.execute(sql, tuple(valores))
    con.commit()


def validar(con):
    """Validaciones del DW: conteos, integridad referencial y vista."""
    cur = con.cursor()
    resumen = {}
    for tabla in list(DIMS.keys()) + ['fact_credito']:
        resumen[tabla] = cur.execute(f'SELECT COUNT(*) FROM {tabla}').fetchone()[0]
    resumen['dm_riesgo_crediticio'] = cur.execute(
        'SELECT COUNT(*) FROM dm_riesgo_crediticio').fetchone()[0]
    # integridad referencial (requiere PRAGMA foreign_keys=ON por conexion)
    violaciones = cur.execute('PRAGMA foreign_key_check').fetchall()
    # sin huerfanos por FKs nulas inesperadas
    nulos = cur.execute(
        'SELECT COUNT(*) FROM fact_credito WHERE sk_cliente IS NULL '
        'OR sk_cuenta IS NULL OR sk_hist IS NULL OR sk_proposito IS NULL '
        'OR sk_bien IS NULL OR sk_plan IS NULL OR sk_deudor IS NULL '
        'OR sk_vivienda IS NULL').fetchone()[0]
    return resumen, violaciones, nulos


def main():
    df = pd.read_csv(CSV_PATH)
    print('dataset procesado:', df.shape)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute('PRAGMA foreign_keys = ON')
        crear_esquema(con)

        mapas = {}
        for tabla, cfg in DIMS.items():
            mapas[tabla] = cargar_dimension(con, df, tabla, cfg)
            print(f'{tabla}: {len(mapas[tabla])} filas')

        cargar_hechos(con, df, mapas)
        print('fact_credito cargada')

        resumen, violaciones, nulos = validar(con)
        print('--- validaciones ---')
        for tabla, n in resumen.items():
            print(f'  {tabla}: {n} filas')
        print('  foreign_key_check:', 'sin violaciones' if not violaciones else violaciones)
        print('  FKs nulas en hechos:', nulos)
        ok = (resumen['fact_credito'] == len(df)
              and resumen['dm_riesgo_crediticio'] == len(df)
              and not violaciones and nulos == 0)
        print('DW OK' if ok else 'DW CON PROBLEMAS')
        return ok
    finally:
        con.close()


if __name__ == '__main__':
    main()
