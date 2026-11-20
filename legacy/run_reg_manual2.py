import pandas as pd
import numpy as np
import os
import pickle

df = pd.read_csv("data/processed/south_german_credit_processed.csv")

num_feats = ["laufzeit", "alter"]
cat_feats = ["laufkont_cat", "moral_cat", "verw_cat", "sparkont_cat", "beszeit_cat", 
             "rate_cat", "famges_cat", "buerge_cat", "wohnzeit_cat", "verm_cat", 
             "weitkred_cat", "wohn_cat", "bishkred_cat", "beruf_cat", "pers_cat", 
             "telef_cat", "gastarb_cat"]

df_enc = pd.get_dummies(df[num_feats + cat_feats], columns=cat_feats)
feature_names = list(df_enc.columns)
X = df_enc.astype(float).values
y = df["hoehe"].values.astype(float)

np.random.seed(42)
idx = np.arange(len(X))
np.random.shuffle(idx)
split = int(0.8 * len(X))
train_idx, test_idx = idx[:split], idx[split:]
X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

X_train_b = np.column_stack([np.ones(X_train.shape[0]), X_train])
X_test_b = np.column_stack([np.ones(X_test.shape[0]), X_test])

theta, _, _, _ = np.linalg.lstsq(X_train_b, y_train, rcond=None)
y_pred = X_test_b @ theta

mae = np.mean(np.abs(y_test - y_pred))
rmse = np.sqrt(np.mean((y_test - y_pred)**2))
ss_res = np.sum((y_test - y_pred)**2)
ss_tot = np.sum((y_test - np.mean(y_test))**2)
r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0

print(f"LinearRegression (manual): MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.3f}")

os.makedirs("modelos/regresion", exist_ok=True)
model_data = {"theta": theta, "feature_names": feature_names, "type": "linear_manual"}
with open("modelos/regresion/regresion_linear_manual_amount.pkl", "wb") as f:
    pickle.dump(model_data, f)
print("Guardado: modelos/regresion/regresion_linear_manual_amount.pkl")
