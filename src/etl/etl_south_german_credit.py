"""
ETL South German Credit
Extrae datos crudos, decodifica según codetable, genera dataset procesado y prepara carga a DW.
"""
import os
import pandas as pd

RAW_PATH = os.path.join('data', 'raw', 'SouthGermanCredit.asc')
PROCESSED_DIR = os.path.join('data', 'processed')
OUT_CSV = os.path.join(PROCESSED_DIR, 'south_german_credit_processed.csv')
OUT_PARQUET = os.path.join(PROCESSED_DIR, 'south_german_credit_processed.parquet')

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

def extract():
    df = pd.read_csv(RAW_PATH, sep=' ')
    return df

def transform(df):
    df_dec = df.copy()
    for col,m in MAPPINGS.items():
        if col in df_dec.columns:
            df_dec[col + '_cat'] = df_dec[col].map(m)
    return df_dec

def load(df_dec):
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
    out = load(df_dec)
    print('ETL completado:', out)

if __name__ == '__main__':
    run()
