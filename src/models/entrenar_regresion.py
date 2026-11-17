"""
Regresión del monto del crédito (`hoehe`) — South German Credit
Unidad III / Fase 3. Pipeline estándar de scikit-learn.

Objetivo: predecir el monto solicitado a partir del perfil del cliente
known-at-application. Se excluyen variables de fuga (leakage):
  - `kredit` / `kredit_cat` (resultado del contrato, posterior a la solicitud)
  - `cuota_aprox_mensual` (función determinista de hoehe/laufzeit)

Uso:
    py src/models/entrenar_regresion.py
Salidas:
    modelos/regresion/ridge_amount.pkl            (mejor modelo)
    modelos/regresion/metricas.json               (métricas auditable)
    docs/modelos/figuras/reg_pred_vs_real.png
    docs/modelos/figuras/reg_residuos.png
"""
import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge, RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CSV_PATH = os.path.join('data', 'processed', 'south_german_credit_processed.csv')
OUT_DIR = os.path.join('modelos', 'regresion')
FIG_DIR = os.path.join('docs', 'modelos', 'figuras')

TARGET = 'hoehe'
NUM_FEATS = ['laufzeit', 'alter']
CAT_FEATS = ['laufkont_cat', 'moral_cat', 'verw_cat', 'sparkont_cat',
             'beszeit_cat', 'rate_cat', 'famges_cat', 'buerge_cat',
             'wohnzeit_cat', 'verm_cat', 'weitkred_cat', 'wohn_cat',
             'bishkred_cat', 'beruf_cat', 'pers_cat', 'telef_cat',
             'gastarb_cat']
FEATURES = NUM_FEATS + CAT_FEATS
LEAKS = ['kredit', 'kredit_cat', 'cuota_aprox_mensual']


def cargar_dataset():
    df = pd.read_csv(CSV_PATH)
    return df


def X_y(df):
    X = df[FEATURES]
    y = df[TARGET]
    return X, y


def construir_pipeline(modelo):
    prep = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), CAT_FEATS),
            ('num', StandardScaler(), NUM_FEATS),
        ],
        remainder='drop',
    )
    return Pipeline([('prep', prep), ('modelo', modelo)])


def comparar_modelos(X_train, y_train, semilla=42):
    """CV 5-fold con 3 candidatos + baseline. Devuelve DataFrame ordenado."""
    candidatos = {
        'baseline_mediana': DummyRegressor(strategy='median'),
        'lineal_ols': LinearRegression(),
        'ridge_a1': Ridge(alpha=1.0, random_state=semilla),
        'ridge_cv': RidgeCV(alphas=np.logspace(-3, 3, 13)),
    }
    scoring = {'rmse': 'neg_root_mean_squared_error',
               'mae': 'neg_mean_absolute_error',
               'r2': 'r2'}
    filas = []
    for nombre, modelo in candidatos.items():
        pipe = construir_pipeline(modelo)
        cv = KFold(n_splits=5, shuffle=True, random_state=semilla)
        res = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring)
        filas.append({
            'modelo': nombre,
            'rmse_cv': -res['test_rmse'].mean(),
            'rmse_std': res['test_rmse'].std(),
            'mae_cv': -res['test_mae'].mean(),
            'r2_cv': res['test_r2'].mean(),
        })
    return pd.DataFrame(filas).sort_values('rmse_cv').reset_index(drop=True)


def evaluar_test(pipe, X_train, y_train, X_test, y_test):
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    return {
        'mae_test': float(mean_absolute_error(y_test, pred)),
        'rmse_test': float(np.sqrt(mean_squared_error(y_test, pred))),
        'r2_test': float(r2_score(y_test, pred)),
    }, pred


def coeficientes_estandarizados(pipe):
    """Coeficientes con nombres legibles (numéricas ya estandarizadas)."""
    nombres = pipe.named_steps['prep'].get_feature_names_out()
    coefs = pipe.named_steps['modelo'].coef_
    tabla = (pd.DataFrame({'feature': nombres, 'coef': coefs})
             .assign(abs_coef=lambda d: d['coef'].abs())
             .sort_values('abs_coef', ascending=False)
             .drop(columns='abs_coef')
             .reset_index(drop=True))
    return tabla


def graficar_diagnostico(y_test, pred):
    os.makedirs(FIG_DIR, exist_ok=True)
    rutas = []

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(y_test, pred, alpha=0.5, s=25, color='#4C72B0')
    lim = [min(y_test.min(), pred.min()), max(y_test.max(), pred.max())]
    ax.plot(lim, lim, '--', color='#C44E52', label='predicción perfecta')
    ax.set_title('Regresión del monto: real vs. predicho (test)')
    ax.set_xlabel('Monto real (hoehe, DM)')
    ax.set_ylabel('Monto predicho (DM)')
    ax.legend()
    fig.tight_layout()
    ruta1 = os.path.join(FIG_DIR, 'reg_pred_vs_real.png')
    fig.savefig(ruta1, dpi=150)
    plt.close(fig)
    rutas.append(ruta1)

    residuos = y_test - pred
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(residuos, bins=30, color='#4C72B0', edgecolor='white')
    ax.axvline(0, color='#C44E52', linestyle='--')
    ax.set_title('Residuos de la regresión del monto (test)')
    ax.set_xlabel('Residuo = real − predicho (DM)')
    ax.set_ylabel('Frecuencia')
    fig.tight_layout()
    ruta2 = os.path.join(FIG_DIR, 'reg_residuos.png')
    fig.savefig(ruta2, dpi=150)
    plt.close(fig)
    rutas.append(ruta2)
    return rutas


def main(semilla=42):
    df = cargar_dataset()
    X, y = X_y(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=semilla)

    print('=== Comparación por CV 5-fold (train) ===')
    tabla = comparar_modelos(X_train, y_train, semilla)
    print(tabla.round(2).to_string(index=False))

    mejor = tabla.iloc[0]['modelo']
    print('\nmejor por CV RMSE:', mejor)

    modelos = {
        'baseline_mediana': DummyRegressor(strategy='median'),
        'lineal_ols': LinearRegression(),
        'ridge_a1': Ridge(alpha=1.0, random_state=semilla),
        'ridge_cv': RidgeCV(alphas=np.logspace(-3, 3, 13)),
    }
    pipe = construir_pipeline(modelos[mejor])
    metricas, pred = evaluar_test(pipe, X_train, y_train, X_test, y_test)
    print('=== Métricas en test ===')
    print({k: round(v, 3) for k, v in metricas.items()})

    top = coeficientes_estandarizados(pipe).head(10)
    print('\n=== Top 10 coeficientes (estandarizados) ===')
    print(top.round(1).to_string(index=False))

    rutas = graficar_diagnostico(y_test.reset_index(drop=True),
                                 pd.Series(pred))
    print('\nfiguras:', rutas)

    os.makedirs(OUT_DIR, exist_ok=True)
    nombre_modelo = 'ridge_amount.pkl' if 'ridge' in mejor else 'lineal_amount.pkl'
    ruta_modelo = os.path.join(OUT_DIR, nombre_modelo)
    joblib.dump(pipe, ruta_modelo)

    alpha = getattr(pipe.named_steps['modelo'], 'alpha_', None)
    salida = {
        'fecha': pd.Timestamp.now().isoformat(timespec='seconds'),
        'dataset': CSV_PATH,
        'target': TARGET,
        'features': FEATURES,
        'excluidas_por_leakage': LEAKS,
        'split': {'test_size': 0.2, 'random_state': semilla},
        'cv': {'n_splits': 5, 'shuffle': True},
        'comparacion_cv': tabla.round(3).to_dict(orient='records'),
        'mejor_modelo': mejor,
        'alpha_seleccionado': float(alpha) if alpha is not None else None,
        'metricas_test': metricas,
        'top10_coeficientes': top.round(2).to_dict(orient='records'),
        'modelo_guardado': ruta_modelo,
        'figuras': rutas,
    }
    ruta_json = os.path.join(OUT_DIR, 'metricas.json')
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print('metricas guardadas:', ruta_json)
    return salida


if __name__ == '__main__':
    main()
