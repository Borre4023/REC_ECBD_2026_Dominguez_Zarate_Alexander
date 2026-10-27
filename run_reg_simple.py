import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

df = pd.read_csv("data/processed/south_german_credit_processed.csv")
print(df.shape)

num_feats = ["laufzeit", "alter"]
cat_feats = ["laufkont_cat", "moral_cat", "verw_cat", "sparkont_cat", "beszeit_cat", 
             "rate_cat", "famges_cat", "buerge_cat", "wohnzeit_cat", "verm_cat", 
             "weitkred_cat", "wohn_cat", "bishkred_cat", "beruf_cat", "pers_cat", 
             "telef_cat", "gastarb_cat"]
X = df[num_feats + cat_feats]
y = df["hoehe"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(X_train.shape, X_test.shape)

preprocessor = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), cat_feats)],
    remainder="passthrough"
)

models = {
    "LinearRegression": LinearRegression(),
    "Ridge": Ridge(alpha=1.0, random_state=42),
    "Lasso": Lasso(alpha=1.0, random_state=42)
}

results = []
for name, model in models.items():
    pipe = Pipeline([("prep", preprocessor), ("model", model)])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    results.append({"Modelo": name, "MAE": mae, "RMSE": rmse, "R2": r2})
    print(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.3f}")

print(pd.DataFrame(results))

best = min(results, key=lambda x: x["RMSE"])
print("Mejor:", best)
best_model_name = best["Modelo"]
best_pipe = Pipeline([("prep", preprocessor), ("model", models[best_model_name])])
best_pipe.fit(X_train, y_train)

os.makedirs("modelos/regresion", exist_ok=True)
out_path = f"modelos/regresion/regresion_{best_model_name.lower()}_amount.pkl"
joblib.dump(best_pipe, out_path)
print("Guardado:", out_path)
