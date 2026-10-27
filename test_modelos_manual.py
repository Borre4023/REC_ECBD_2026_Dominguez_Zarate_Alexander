import pickle
import pandas as pd
import numpy as np

# =========================
# 1) CARGAR MODELOS
# =========================
with open("modelos/regresion/regresion_linear_manual_amount.pkl", "rb") as f:
    reg_model = pickle.load(f)

with open("modelos/clasificacion/clasificacion_logistic_manual_creditrisk.pkl", "rb") as f:
    clas_model = pickle.load(f)

print("Modelos cargados correctamente")
print("Regresión tipo:", reg_model["type"])
print("Clasificación tipo:", clas_model["type"])
print("-" * 60)

# =========================
# 2) CARGAR DATOS PROCESADOS
# =========================
df = pd.read_csv("data/processed/south_german_credit_processed.csv")

# Mismas features que se usaron al entrenar
num_feats_reg = ["laufzeit", "alter"]
cat_feats_reg = ["laufkont_cat", "moral_cat", "verw_cat", "sparkont_cat", "beszeit_cat", 
                 "rate_cat", "famges_cat", "buerge_cat", "wohnzeit_cat", "verm_cat", 
                 "weitkred_cat", "wohn_cat", "bishkred_cat", "beruf_cat", "pers_cat", 
                 "telef_cat", "gastarb_cat"]

num_feats_clas = ["laufzeit", "hoehe", "alter"]
cat_feats_clas = ["laufkont_cat", "moral_cat", "verw_cat", "sparkont_cat", "beszeit_cat", 
                  "rate_cat", "famges_cat", "buerge_cat", "wohnzeit_cat", "verm_cat", 
                  "weitkred_cat", "wohn_cat", "bishkred_cat", "beruf_cat", "pers_cat", 
                  "telef_cat", "gastarb_cat"]

# One-hot encoding idéntico al entrenamiento
df_reg_enc = pd.get_dummies(df[num_feats_reg + cat_feats_reg], columns=cat_feats_reg)
df_clas_enc = pd.get_dummies(df[num_feats_clas + cat_feats_clas], columns=cat_feats_clas)

# Alinear columnas con las que se guardaron
X_reg = df_reg_enc.reindex(columns=reg_model["feature_names"], fill_value=0).astype(float).values
X_clas = df_clas_enc.reindex(columns=clas_model["feature_names"], fill_value=0).astype(float).values

# =========================
# 3) COMPROBAR REGRESIÓN (predecir monto)
# =========================
theta = reg_model["theta"]
X_reg_b = np.column_stack([np.ones(X_reg.shape[0]), X_reg])
y_pred_reg = X_reg_b @ theta

print("=== COMPROBACIÓN REGRESIÓN ===")
print("Predicciones para los primeros 5 registros:")
for i in range(5):
    print(f"Registro {i+1} -> Monto real: {df['hoehe'].iloc[i]:.0f} DM | Monto predicho: {y_pred_reg[i]:.0f} DM")
print("-" * 60)

# =========================
# 4) COMPROBAR CLASIFICACIÓN (predecir riesgo)
# =========================
w = clas_model["w"]
X_clas_b = np.column_stack([np.ones(X_clas.shape[0]), X_clas])
z = X_clas_b @ w
p = 1 / (1 + np.exp(-np.clip(z, -250, 250)))
y_pred_clas = (p >= 0.5).astype(int)

print("=== COMPROBACIÓN CLASIFICACIÓN ===")
print("Predicciones para los primeros 10 registros (1 = good, 0 = bad):")
for i in range(10):
    real = df['kredit'].iloc[i]
    print(f"Registro {i+1} -> Real: {real} ({'good' if real==1 else 'bad'}) | Predicho: {y_pred_clas[i]} ({'good' if y_pred_clas[i]==1 else 'bad'}) | Prob(good): {p[i]:.3f}")
print("-" * 60)
print("Prueba finalizada correctamente.")