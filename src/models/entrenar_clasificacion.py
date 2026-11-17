"""
Clasificación del riesgo crediticio (`kredit`) — South German Credit
Unidad III / Fase 3. Pipeline estándar de scikit-learn.

Objetivo: predecir si un crédito será malo (kredit=0, "bad") a partir del
perfil del cliente known-at-application. Se excluyen fugas (leakage):
  - `kredit` / `kredit_cat` (objetivo)
  - `cuota_aprox_mensual` (deriva del monto/plazo, no disponible igual en producción)

Diseño:
  - Clase positiva = "bad" (0): lo que interesa detectar en un banco.
  - class_weight='balanced' por el desbalance 700/300.
  - CV estratificada 5-fold por ROC-AUC.
  - Umbral óptimo por F1 de "bad" con cross_val_predict en train (sin tocar test).

Uso:
    py src/models/entrenar_clasificacion.py
Salidas:
    modelos/clasificacion/mejor_riesgo.pkl
    modelos/clasificacion/metricas.json
    docs/modelos/figuras/roc_curvas.png
    docs/modelos/figuras/matriz_confusion.png
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
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import (StratifiedKFold, cross_val_predict,
                                     cross_validate, train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CSV_PATH = os.path.join('data', 'processed', 'south_german_credit_processed.csv')
OUT_DIR = os.path.join('modelos', 'clasificacion')
FIG_DIR = os.path.join('docs', 'modelos', 'figuras')

TARGET = 'kredit'          # 0 = bad (positiva de interés), 1 = good
POSA_LABEL = 0             # clase positiva: bad
NUM_FEATS = ['laufzeit', 'hoehe', 'alter']
CAT_FEATS = ['laufkont_cat', 'moral_cat', 'verw_cat', 'sparkont_cat',
             'beszeit_cat', 'rate_cat', 'famges_cat', 'buerge_cat',
             'wohnzeit_cat', 'verm_cat', 'weitkred_cat', 'wohn_cat',
             'bishkred_cat', 'beruf_cat', 'pers_cat', 'telef_cat',
             'gastarb_cat']
FEATURES = NUM_FEATS + CAT_FEATS
EXCLUIDAS = ['kredit', 'kredit_cat', 'cuota_aprox_mensual']


def construir_pipeline(modelo):
    prep = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), CAT_FEATS),
            ('num', StandardScaler(), NUM_FEATS),
        ],
        remainder='drop',
    )
    return Pipeline([('prep', prep), ('modelo', modelo)])


def candidatos(semilla):
    return {
        'baseline_mayoritaria': DummyClassifier(strategy='prior'),
        'logistica_bal_C1': LogisticRegression(
            max_iter=2000, class_weight='balanced', C=1.0, random_state=semilla),
        'logistica_bal_C01': LogisticRegression(
            max_iter=2000, class_weight='balanced', C=0.1, random_state=semilla),
        'random_forest_bal': RandomForestClassifier(
            n_estimators=300, class_weight='balanced',
            random_state=semilla, n_jobs=-1),
    }


def comparar_modelos(X_train, y_train, semilla=42):
    """CV estratificada 5-fold por ROC-AUC. Devuelve DataFrame ordenado."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=semilla)
    filas = []
    for nombre, modelo in candidatos(semilla).items():
        pipe = construir_pipeline(modelo)
        res = cross_validate(pipe, X_train, y_train, cv=cv,
                             scoring={'auc': 'roc_auc',
                                      'f1_bad': 'f1'})
        filas.append({
            'modelo': nombre,
            'roc_auc_cv': res['test_auc'].mean(),
            'auc_std': res['test_auc'].std(),
            'f1_bad_cv': res['test_f1_bad'].mean(),
        })
    return (pd.DataFrame(filas)
              .sort_values('roc_auc_cv', ascending=False)
              .reset_index(drop=True))


def umbral_optimo(pipe, X_train, y_train, semilla=42):
    """Umbral que maximiza F1 de 'bad' usando cross_val_predict en train."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=semilla)
    # columna de la clase positiva en predict_proba: classes_=[0,1] => bad=col 0
    clases = pipe.fit(X_train, y_train).named_steps['modelo'].classes_
    idx_bad = int(np.where(clases == POSA_LABEL)[0][0])
    proba_bad = cross_val_predict(
        pipe, X_train, y_train, cv=cv, method='predict_proba')[:, idx_bad]

    umbrales = np.linspace(0.05, 0.95, 181)
    f1s = [f1_score(y_train == POSA_LABEL, proba_bad >= u) for u in umbrales]
    mejor_i = int(np.argmax(f1s))
    return float(umbrales[mejor_i]), float(f1s[mejor_i]), proba_bad


def evaluar_test(pipe, umbral, X_train, y_train, X_test, y_test):
    pipe.fit(X_train, y_train)
    clases = pipe.named_steps['modelo'].classes_
    idx_bad = int(np.where(clases == POSA_LABEL)[0][0])
    proba_bad = pipe.predict_proba(X_test)[:, idx_bad]
    pred_bad = (proba_bad >= umbral).astype(int)   # 1 = predice bad
    y_true_bad = (y_test == POSA_LABEL).astype(int)
    return {
        'roc_auc_test': float(roc_auc_score(y_true_bad, proba_bad)),
        'umbral': umbral,
        'precision_bad': float(precision_score(y_true_bad, pred_bad)),
        'recall_bad': float(recall_score(y_true_bad, pred_bad)),
        'f1_bad': float(f1_score(y_true_bad, pred_bad)),
    }, y_true_bad, pred_bad, proba_bad


def probas_todos(X_train, y_train, X_test, semilla=42):
    """Proba de 'bad' en test para cada candidato (para las curvas ROC)."""
    probas, nombres = [], []
    for nombre, m in candidatos(semilla).items():
        p = construir_pipeline(m).fit(X_train, y_train)
        clases = p.named_steps['modelo'].classes_
        idx_bad = int(np.where(clases == POSA_LABEL)[0][0])
        probas.append(p.predict_proba(X_test)[:, idx_bad])
        nombres.append(nombre)
    return probas, nombres


def top_variables(pipe, n=12):
    """Importancias legibles: coeficientes (logística) o feature_importances (RF)."""
    nombres = pipe.named_steps['prep'].get_feature_names_out()
    modelo = pipe.named_steps['modelo']
    if hasattr(modelo, 'feature_importances_'):
        vals = modelo.feature_importances_
    else:
        vals = np.abs(modelo.coef_[0])
    return (pd.DataFrame({'feature': nombres, 'importancia': vals})
              .sort_values('importancia', ascending=False)
              .head(n)
              .reset_index(drop=True))


def graficar(y_test_bad, proba_test, proba_curvas, nombres_curvas, umbral,
             y_pred_bad, ruta_fig):
    os.makedirs(FIG_DIR, exist_ok=True)
    rutas = []

    # ROC de todos los modelos en test + diagonal
    fig, ax = plt.subplots(figsize=(7, 6))
    for nombre, proba in zip(nombres_curvas, proba_curvas):
        fpr, tpr, _ = roc_curve(y_test_bad, proba)
        auc = roc_auc_score(y_test_bad, proba)
        ax.plot(fpr, tpr, label=f'{nombre} (AUC={auc:.3f})')
    ax.plot([0, 1], [0, 1], '--', color='gray', label='azar (AUC=0.5)')
    ax.set_title('Curvas ROC en test — riesgo crediticio (bad=positiva)')
    ax.set_xlabel('FPR (good mal clasificados)')
    ax.set_ylabel('TPR (bad detectados)')
    ax.legend(loc='lower right')
    fig.tight_layout()
    ruta1 = os.path.join(FIG_DIR, 'roc_curvas.png')
    fig.savefig(ruta1, dpi=150)
    plt.close(fig)
    rutas.append(ruta1)

    # Matriz de confusión con el umbral óptimo (labels=[1,0]: bad primero)
    cm = confusion_matrix(y_test_bad, y_pred_bad, labels=[1, 0])
    # cm = [[TP, FN], [FP, TN]] con bad como clase positiva
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    im = ax.imshow(cm, cmap='Blues')
    etiquetas = ['real bad', 'real good']
    pred_labels = ['pred bad', 'pred good']
    ax.set_xticks([0, 1], pred_labels)
    ax.set_yticks([0, 1], etiquetas)
    for i in range(2):
        for j in range(2):
            color = 'white' if cm[i, j] > cm.max() / 2 else 'black'
            ax.text(j, i, str(cm[i, j]), ha='center', va='center', color=color,
                    fontsize=16)
    ax.set_title(f'Matriz de confusión (umbral={umbral:.2f})')
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    ruta2 = os.path.join(FIG_DIR, 'matriz_confusion.png')
    fig.savefig(ruta2, dpi=150)
    plt.close(fig)
    rutas.append(ruta2)
    return rutas


def main(semilla=42):
    df = pd.read_csv(CSV_PATH)
    X, y = df[FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=semilla, stratify=y)

    print('=== Comparación por CV estratificada 5-fold (train) ===')
    tabla = comparar_modelos(X_train, y_train, semilla)
    print(tabla.round(3).to_string(index=False))
    mejor = tabla.iloc[0]['modelo']
    print('\nmejor por CV ROC-AUC:', mejor)

    modelos = candidatos(semilla)
    pipe = construir_pipeline(modelos[mejor])

    # probas de TODOS los modelos en test (para las curvas ROC)
    y_test_bad = (y_test == POSA_LABEL).astype(int).to_numpy()
    proba_curvas, nombres_curvas = probas_todos(X_train, y_train, X_test, semilla)

    umbral, f1_cv, proba_bad_cv = umbral_optimo(pipe, X_train, y_train, semilla)
    print(f'\numbral óptimo (F1-bad en CV train): {umbral:.2f} (F1={f1_cv:.3f})')

    metricas, y_true_bad, pred_bad, proba_test = evaluar_test(
        pipe, umbral, X_train, y_train, X_test, y_test)
    print('=== Métricas en test (umbral óptimo) ===')
    print({k: round(v, 3) for k, v in metricas.items()})

    top = top_variables(pipe, 12)
    print('\n=== Top 12 variables ===')
    print(top.round(3).to_string(index=False))

    rutas = graficar(y_test_bad, proba_test, proba_curvas, nombres_curvas,
                     umbral, pred_bad, FIG_DIR)
    print('\nfiguras:', rutas)

    os.makedirs(OUT_DIR, exist_ok=True)
    ruta_modelo = os.path.join(OUT_DIR, 'mejor_riesgo.pkl')
    joblib.dump(pipe, ruta_modelo)

    salida = {
        'fecha': pd.Timestamp.now().isoformat(timespec='seconds'),
        'dataset': CSV_PATH,
        'target': TARGET,
        'clase_positiva': 'bad (kredit=0)',
        'features': FEATURES,
        'excluidas': EXCLUIDAS,
        'split': {'test_size': 0.2, 'random_state': semilla, 'stratify': True},
        'cv': {'n_splits': 5, 'estratificada': True},
        'comparacion_cv': tabla.round(3).to_dict(orient='records'),
        'mejor_modelo': mejor,
        'umbral_optimo': umbral,
        'f1_bad_cv': f1_cv,
        'metricas_test': metricas,
        'matriz_confusion_test': confusion_matrix(
            y_true_bad, pred_bad, labels=[1, 0]).tolist(),  # [[TP,FN],[FP,TN]]
        'top_variables': top.round(3).to_dict(orient='records'),
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
