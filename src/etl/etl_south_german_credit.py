"""
ETL South German Credit (consolidado - Fase 1)
Extrae datos crudos, decodifica segun codetable, agrega variable derivada,
ejecuta validaciones de calidad y guarda el dataset procesado + reporte JSON.

Uso:
    py src/etl/etl_south_german_credit.py
Salidas:
    data/processed/south_german_credit_processed.csv
    data/processed/south_german_credit_processed.parquet
    data/processed/reporte_calidad_etl.json
"""
import json
import os

import pandas as pd

RAW_PATH = os.path.join('data', 'raw', 'SouthGermanCredit.asc')
PROCESSED_DIR = os.path.join('data', 'processed')
OUT_CSV = os.path.join(PROCESSED_DIR, 'south_german_credit_processed.csv')
OUT_PARQUET = os.path.join(PROCESSED_DIR, 'south_german_credit_processed.parquet')
OUT_REPORT = os.path.join(PROCESSED_DIR, 'reporte_calidad_etl.json')

MAPPINGS = {
  'laufkont': {1:'no_checking',2:'lt0',3:'0_to_200',4:'ge200_or_salary'},
  'moral': {0:'delay',1:'critical',2:'no_credits_or_paid',3:'existing_paid',4:'all_bank_paid'},
  'verw': {0:'others',1:'car_new',2:'car_used',3:'furniture',4:'radio_tv',5:'appliances',6:'repairs',7:'education',8:'vacation',9:'retraining',10:'business'},
  'sparkont': {1:'unknown',2:'lt100',3:'100_to_500',4:'500_to_1000',5:'ge1000'},
  'beszeit': {1:'unemployed',2:'lt1',3:'1_to_4',4:'4_to_7',5:'ge7'},
  'rate': {1:'ge35',2:'25_to_35',3:'20_to_25',4:'lt20'},
  'famges': {1:'male_divorced_sep',2:'female_nonsingle_or_male_single',3:'male_married_widowed',4:'female_single'},
  'buerge': {1:'none',2:'coapplicant',3:'guarantor'},
  'wohnzeit': {1:'lt1',2:'1_to_4',3:'4_to_7',4:'ge7'},
  'verm': {1:'unknown',2:'car_other',3:'life_insurance',4:'real_estate'},
  'weitkred': {1:'bank',2:'stores',3:'none'},
  'wohn': {1:'free',2:'rent',3:'own'},
  'bishkred': {1:'1',2:'2_3',3:'4_5',4:'ge6'},
  'beruf': {1:'unskilled_nonresident',2:'unskilled_resident',3:'skilled_official',4:'high_qual_selfemp'},
  'pers': {1:'ge3',2:'0_to_2'},
  'telef': {1:'no',2:'yes'},
  'gastarb': {1:'yes',2:'no'},
  'kredit': {0:'bad',1:'good'}
}

# Rangos de codigos validos (fuente: data/raw/codetable.txt)
CODIGOS_VALIDOS = {
    'laufkont': range(1, 5), 'moral': range(0, 5), 'verw': range(0, 11),
    'sparkont': range(1, 6), 'beszeit': range(1, 6), 'rate': range(1, 5),
    'famges': range(1, 5), 'buerge': range(1, 4), 'wohnzeit': range(1, 5),
    'verm': range(1, 5), 'weitkred': range(1, 4), 'wohn': range(1, 4),
    'bishkred': range(1, 5), 'beruf': range(1, 5), 'pers': range(1, 3),
    'telef': range(1, 3), 'gastarb': range(1, 3), 'kredit': range(0, 2),
}


def extract():
    """Extract: lectura del archivo crudo delimitado por espacios."""
    df = pd.read_csv(RAW_PATH, sep=' ')
    return df


def transform(df):
    """Transform: decodificacion *_cat, variable derivada de cuota."""
    df_dec = df.copy()
    for col, m in MAPPINGS.items():
        if col in df_dec.columns:
            df_dec[col + '_cat'] = df_dec[col].map(m)
    # Variable derivada: carga mensual aproximada del credito
    df_dec['cuota_aprox_mensual'] = (df_dec['hoehe'] / df_dec['laufzeit']).round(2)
    return df_dec


def validate(df_raw, df_dec):
    """Validaciones de calidad post-ETL. Devuelve (reporte_dict, todo_ok)."""
    reporte = {}
    cheques = []

    def check(nombre, ok, detalle):
        cheques.append({'check': nombre, 'ok': bool(ok), 'detalle': detalle})
        return ok

    # 1) filas conservadas
    check('filas_conservadas', len(df_raw) == len(df_dec) == 1000,
          f"raw={len(df_raw)} dec={len(df_dec)} esperado=1000")

    # 2) sin valores faltantes
    nulos = int(df_dec.isnull().sum().sum())
    check('sin_nulos', nulos == 0, f'total_nulos={nulos}')

    # 3) sin duplicados exactos
    dups = int(df_dec.duplicated().sum())
    check('sin_duplicados', dups == 0, f'duplicados={dups}')

    # 4) codigos dentro de catalogo
    fuera = {}
    for col, codigos in CODIGOS_VALIDOS.items():
        invalidos = df_raw.loc[~df_raw[col].isin(codigos), col]
        if len(invalidos):
            fuera[col] = sorted(set(invalidos.unique()))
    check('codigos_en_catalogo', len(fuera) == 0,
          f'columnas_con_codigos_invalidos={list(fuera) or "ninguna"}')

    # 5) decodificacion completa (ninguna *_cat con NaN)
    sin_decodificar = [c for c in df_dec.columns
                       if c.endswith('_cat') and df_dec[c].isnull().any()]
    check('decodificacion_completa', len(sin_decodificar) == 0,
          f'columnas_sin_decodificar={sin_decodificar or "ninguna"}')

    # 6) variable derivada consistente
    recalc = (df_dec['hoehe'] / df_dec['laufzeit']).round(2)
    check('cuota_aprox_consistente',
          bool((recalc == df_dec['cuota_aprox_mensual']).all()),
          'cuota_aprox_mensual = hoehe / laufzeit (redondeo 2 decimales)')

    # 7) rangos logicos de cuantitativas
    logicas = {
        'laufzeit': df_dec['laufzeit'].between(1, 120).all(),
        'hoehe': (df_dec['hoehe'] > 0).all(),
        'alter': df_dec['alter'].between(18, 100).all(),
    }
    check('rangos_logicos_ok', all(logicas.values()),
          {k: bool(v) for k, v in logicas.items()})

    reporte['fecha'] = pd.Timestamp.now().isoformat(timespec='seconds')
    reporte['shape_entrada'] = list(df_raw.shape)
    reporte['shape_salida'] = list(df_dec.shape)
    reporte['columnas_nuevas'] = sorted(
        set(df_dec.columns) - set(df_raw.columns))
    reporte['cheques'] = cheques
    reporte['todo_ok'] = all(c['ok'] for c in cheques)
    return reporte


def load(df_dec):
    """Load: CSV + Parquet + reporte de calidad JSON."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df_dec.to_csv(OUT_CSV, index=False)
    try:
        df_dec.to_parquet(OUT_PARQUET, index=False)
    except Exception as e:
        print('No se pudo guardar parquet:', e)
    return OUT_CSV


def run():
    df = extract()
    df_dec = transform(df)
    reporte = validate(df, df_dec)
    out = load(df_dec)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(OUT_REPORT, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    print('ETL completado:', out)
    print(f"shape: {df_dec.shape[0]} filas x {df_dec.shape[1]} columnas")
    for c in reporte['cheques']:
        estado = 'OK ' if c['ok'] else 'FALLA'
        print(f"  [{estado}] {c['check']}: {c['detalle']}")
    print('Reporte de calidad:', OUT_REPORT)
    return df_dec


if __name__ == '__main__':
    run()
