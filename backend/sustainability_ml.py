import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# 📂 Load dataset
print("📂 Loading dataset...")
df = pd.read_csv("C:\greenbite\datasets\Food_Product_Emissions.csv")

# 🔍 Data Overview
print("\n🔍 Checking dataset info:")
print(df.info())

# 🛠️ Preprocessing
df = df.select_dtypes(include=[np.number])  # Drop non-numeric columns
df.fillna(df.mean(), inplace=True)  # Handle missing values

# 🚀 Features & Target
features = df.drop(columns=["Total Global Average GHG Emissions per kg"], errors='ignore')
target = df["Total Global Average GHG Emissions per kg"]

# 🔬 Feature Scaling
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# 🔄 Train-Test Split for Final Testing
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# 🚀 Model Training & Selection
models = {
    "Random Forest": RandomForestRegressor(
        n_estimators=100, max_depth=5, min_samples_leaf=3, max_features='sqrt', random_state=42
    ),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
}

best_model, best_r2 = None, float('-inf')

for name, model in models.items():
    print(f"⏳ Training {name} with 5-Fold CV...")
    
    # 🎯 Cross-Validation Scores
    r2_scores = cross_val_score(model, features_scaled, target, cv=kf, scoring='r2')
    avg_r2 = np.mean(r2_scores)

    print(f"📊 {name} Evaluation:")
    print(f" - Cross-Validation R² Scores: {r2_scores}")
    print(f" - Average CV R²: {avg_r2:.2f}\n")

    # 📌 Select Best Model
    if avg_r2 > best_r2:
        best_model, best_r2 = model, avg_r2

# ✅ Train Best Model on Full Data
print(f"🏆 Best model selected: {best_model.__class__.__name__}")
best_model.fit(features_scaled, target)

# ✅ Save Model
with open("sustainability_model.pkl", "wb") as f:
    pickle.dump(best_model, f)
print("✅ Best model saved successfully!")
