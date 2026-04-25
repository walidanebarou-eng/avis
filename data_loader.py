# BrewIQ · utils/data_loader.py
import pandas as pd
import numpy as np
from flask import current_app

_df_cache = None


def get_df() -> pd.DataFrame:
    """Charge et cache le DataFrame CSV."""
    global _df_cache
    if _df_cache is None:
        path = current_app.config.get('CSV_PATH', 'data/Coffe_sales_with_reviews.csv')
        _df_cache = pd.read_csv(path)
    return _df_cache.copy()


def sales_summary(df: pd.DataFrame) -> dict:
    return {
        'total_revenue': round(float(df['money'].sum()), 2),
        'total_transactions': int(len(df)),
        'average_basket': round(float(df['money'].mean()), 2),
        'unique_products': int(df['coffee_name'].nunique()),
        'date_range': {
            'start': df['Date'].min(),
            'end': df['Date'].max()
        }
    }


def by_product(df: pd.DataFrame) -> list:
    g = df.groupby('coffee_name')['money'].agg(['sum', 'count', 'mean']).reset_index()
    g.columns = ['product', 'revenue', 'orders', 'avg_price']
    g = g.sort_values('revenue', ascending=False)
    g['revenue']   = g['revenue'].round(2)
    g['avg_price'] = g['avg_price'].round(2)
    return g.to_dict(orient='records')


def by_month(df: pd.DataFrame) -> list:
    g = df.groupby(['month_sort', 'Month_name'])['money'].agg(['sum', 'count']).reset_index()
    g.columns = ['month_sort', 'month_name', 'revenue', 'orders']
    g = g.sort_values('month_sort')
    g['revenue'] = g['revenue'].round(2)
    return g.to_dict(orient='records')


def by_weekday(df: pd.DataFrame) -> list:
    g = df.groupby(['Weekdaysort', 'Weekday'])['money'].agg(['sum', 'count']).reset_index()
    g.columns = ['weekday_sort', 'weekday', 'revenue', 'orders']
    g = g.sort_values('weekday_sort')
    g['revenue'] = g['revenue'].round(2)
    return g.to_dict(orient='records')


def by_hour(df: pd.DataFrame) -> list:
    g = df.groupby('hour_of_day')['money'].agg(['sum', 'count']).reset_index()
    g.columns = ['hour', 'revenue', 'orders']
    g['revenue'] = g['revenue'].round(2)
    return g.to_dict(orient='records')


def by_time_of_day(df: pd.DataFrame) -> list:
    g = df.groupby('Time_of_Day')['money'].agg(['sum', 'count']).reset_index()
    g.columns = ['time_of_day', 'revenue', 'orders']
    g['revenue'] = g['revenue'].round(2)
    return g.to_dict(orient='records')
