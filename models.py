# BrewIQ · app/models.py
from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), default='viewer')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), unique=True, nullable=False)
    category   = db.Column(db.String(50))
    base_price = db.Column(db.Numeric(8, 2))
    icon       = db.Column(db.String(10))
    active     = db.Column(db.Boolean, default=True)
    sales      = db.relationship('Sale', backref='product', lazy=True)
    reviews    = db.relationship('Review', backref='product', lazy=True)

class Sale(db.Model):
    __tablename__ = 'sales'
    id           = db.Column(db.Integer, primary_key=True)
    product_id   = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    sale_date    = db.Column(db.Date, nullable=False)
    sale_time    = db.Column(db.Time)
    hour_of_day  = db.Column(db.SmallInteger)
    time_of_day  = db.Column(db.String(20))
    weekday      = db.Column(db.String(10))
    weekday_sort = db.Column(db.SmallInteger)
    month_name   = db.Column(db.String(10))
    month_sort   = db.Column(db.SmallInteger)
    amount       = db.Column(db.Numeric(8, 2), nullable=False)
    cash_type    = db.Column(db.String(20), default='card')

class Review(db.Model):
    __tablename__ = 'reviews'
    id              = db.Column(db.Integer, primary_key=True)
    sale_id         = db.Column(db.Integer, db.ForeignKey('sales.id'))
    product_id      = db.Column(db.Integer, db.ForeignKey('products.id'))
    review_text     = db.Column(db.Text, nullable=False)
    sentiment       = db.Column(db.String(20))
    sentiment_score = db.Column(db.Numeric(4, 3))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id            = db.Column(db.Integer, primary_key=True)
    product_id    = db.Column(db.Integer, db.ForeignKey('products.id'))
    target_month  = db.Column(db.Date, nullable=False)
    predicted_rev = db.Column(db.Numeric(10, 2))
    predicted_cnt = db.Column(db.Integer)
    confidence    = db.Column(db.Numeric(4, 3))
    model_version = db.Column(db.String(20))
    generated_at  = db.Column(db.DateTime, default=datetime.utcnow)
