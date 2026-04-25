# BrewIQ · config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'brewiq-secret-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost/brewiq'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-brewiq-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    CSV_PATH = os.getenv('CSV_PATH', 'data/Coffe_sales_with_reviews.csv')
