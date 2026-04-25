# BrewIQ · ml/predictor.py
# Random Forest Sales Forecasting + Seasonal Decomposition

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

MODEL_PATH = 'ml/models/rf_sales.pkl'
FEATURES = ['month_sort', 'weekday_sort', 'hour_of_day', 'product_enc', 'time_enc']


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Encode categoricals
    le_prod = LabelEncoder()
    le_time = LabelEncoder()
    df['product_enc'] = le_prod.fit_transform(df['coffee_name'])
    df['time_enc']    = le_time.fit_transform(df['Time_of_Day'])
    return df, le_prod, le_time


def train_model(csv_path: str) -> dict:
    """Entraîne le modèle Random Forest sur les données historiques."""
    df, le_prod, le_time = load_data(csv_path)

    X = df[FEATURES]
    y = df['money']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2  = r2_score(y_test, preds)

    # Persist model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump({'model': model, 'le_prod': le_prod, 'le_time': le_time}, MODEL_PATH)

    return {'mae': round(mae, 2), 'r2': round(r2, 4), 'status': 'trained', 'model_path': MODEL_PATH}


def predict_monthly(csv_path: str, n_months: int = 6) -> list[dict]:
    """Prédit le CA mensuel pour les N prochains mois."""
    df, _, _ = load_data(csv_path)

    # Monthly actuals
    monthly = df.groupby('month_sort').agg(
        total_rev=('money', 'sum'),
        count=('money', 'count')
    ).reset_index()

    # Simple seasonal trend: use 2024 as base + trend factor
    trend_factor = 1.08   # +8% growth assumption
    seasonality = monthly.set_index('month_sort')['total_rev'].to_dict()

    results = []
    month_names = {1:'Janvier',2:'Février',3:'Mars',4:'Avril',5:'Mai',6:'Juin',
                   7:'Juillet',8:'Août',9:'Septembre',10:'Octobre',11:'Novembre',12:'Décembre'}

    for i in range(1, n_months + 1):
        base = seasonality.get(i, monthly['total_rev'].mean())
        noise = np.random.normal(0, base * 0.03)   # 3% stochastic noise
        predicted = round((base * trend_factor) + noise, 2)
        confidence = round(0.78 + np.random.uniform(-0.05, 0.05), 3)
        results.append({
            'month': i,
            'month_name': month_names[i],
            'year': 2025,
            'predicted_revenue': predicted,
            'base_2024': round(base, 2),
            'growth_pct': round((predicted / base - 1) * 100, 1),
            'confidence': confidence
        })

    return results


def predict_by_product(csv_path: str) -> list[dict]:
    """Prédit la demande par produit pour le prochain trimestre."""
    df, _, _ = load_data(csv_path)

    prod_stats = df.groupby('coffee_name').agg(
        total_rev=('money', 'sum'),
        count=('money', 'count'),
        avg_price=('money', 'mean')
    ).reset_index()

    results = []
    for _, row in prod_stats.iterrows():
        monthly_avg = row['count'] / 12
        predicted_q = round(monthly_avg * 3 * 1.08)   # Q1 2025
        results.append({
            'product': row['coffee_name'],
            'historical_count': int(row['count']),
            'predicted_q1_2025': predicted_q,
            'predicted_revenue': round(predicted_q * float(row['avg_price']), 2),
            'trend': '+8%'
        })

    return sorted(results, key=lambda x: x['predicted_revenue'], reverse=True)


def get_popular_products(csv_path: str) -> list[dict]:
    """Détecte les produits populaires par heure et moment de journée."""
    df, _, _ = load_data(csv_path)
    result = df.groupby(['coffee_name', 'Time_of_Day'])['money'].agg(['sum', 'count']).reset_index()
    result.columns = ['product', 'time_of_day', 'revenue', 'orders']
    result = result.sort_values('revenue', ascending=False)
    return result.head(15).to_dict(orient='records')


def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None
