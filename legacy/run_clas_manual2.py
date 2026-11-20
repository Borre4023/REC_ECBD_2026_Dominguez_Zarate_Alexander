import pandas as pd
import numpy as np
import os
import pickle

df = pd.read_csv("data/processed/south_german_credit_processed.csv")

num_feats = ["laufzeit", "hoehe", "alter"]
cat_feats = ["laufkont_cat", "moral_cat", "verw_cat", "sparkont_cat", "beszeit_cat", 
             "rate_cat", "famges_cat", "buerge_cat", "wohnzeit_cat", "verm_cat", 
             "weitkred_cat", "wohn_cat", "bishkred_cat", "beruf_cat", "pers_cat", 
             "telef_cat", "gastarb_cat"]

df_enc = pd.get_dummies(df[num_feats + cat_feats], columns=cat_feats)
feature_names = list(df_enc.columns)
X = df_enc.astype(float).values
y = df["kredit"].values.astype(int)

np.random.seed(42)
idx_good = np.where(y==1)[0]
idx_bad = np.where(y==0)[0]
np.random.shuffle(idx_good)
np.random.shuffle(idx_bad)
n_good_test = int(0.2*len(idx_good))
n_bad_test = int(0.2*len(idx_bad))
test_idx = np.concatenate([idx_good[:n_good_test], idx_bad[:n_bad_test]])
train_idx = np.concatenate([idx_good[n_good_test:], idx_bad[n_bad_test:]])
np.random.shuffle(train_idx)
np.random.shuffle(test_idx)

X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

X_train_b = np.column_stack([np.ones(X_train.shape[0]), X_train])
X_test_b = np.column_stack([np.ones(X_test.shape[0]), X_test])

m, n = X_train_b.shape
w = np.zeros(n)
lr = 0.01
epochs = 3000

for epoch in range(epochs):
    z = X_train_b @ w
    p = 1 / (1 + np.exp(-np.clip(z, -250, 250)))
    grad = X_train_b.T @ (p - y_train) / m
    w -= lr * grad

z_test = X_test_b @ w
p_test = 1 / (1 + np.exp(-np.clip(z_test, -250, 250)))
y_pred = (p_test >= 0.5).astype(int)

tp = np.sum((y_pred==1) & (y_test==1))
tn = np.sum((y_pred==0) & (y_test==0))
fp = np.sum((y_pred==1) & (y_test==0))
fn = np.sum((y_pred==0) & (y_test==1))

acc = (tp+tn)/(tp+tn+fp+fn)
prec = tp/(tp+fp) if (tp+fp)>0 else 0
rec = tp/(tp+fn) if (tp+fn)>0 else 0
f1 = 2*prec*rec/(prec+rec) if (prec+rec)>0 else 0

# AUC manual
order = np.argsort(p_test)
y_sorted = y_test[order]
p_sorted = p_test[order]
tpr_list = []
fpr_list = []
for thresh in np.linspace(0,1,51):
    yp = (p_sorted >= thresh).astype(int)
    tp_t = np.sum((yp==1)&(y_sorted==1))
    fp_t = np.sum((yp==1)&(y_sorted==0))
    tn_t = np.sum((yp==0)&(y_sorted==0))
    fn_t = np.sum((yp==0)&(y_sorted==1))
    tpr_list.append(tp_t/(tp_t+fn_t) if (tp_t+fn_t)>0 else 0)
    fpr_list.append(fp_t/(fp_t+tn_t) if (fp_t+tn_t)>0 else 0)
auc = np.trapz(np.array(tpr_list), np.array(fpr_list)) if hasattr(np, 'trapz') else 0.5

print(f"LogisticRegression (manual): Accuracy={acc:.3f}, Precision={prec:.3f}, Recall={rec:.3f}, F1={f1:.3f}, ROC_AUC={auc:.3f}")
print(f"Confusion: TN={tn}, FP={fp}, FN={fn}, TP={tp}")

os.makedirs("modelos/clasificacion", exist_ok=True)
model_data = {"w": w, "feature_names": feature_names, "type": "logistic_manual"}
with open("modelos/clasificacion/clasificacion_logistic_manual_creditrisk.pkl", "wb") as f:
    pickle.dump(model_data, f)
print("Guardado: modelos/clasificacion/clasificacion_logistic_manual_creditrisk.pkl")
