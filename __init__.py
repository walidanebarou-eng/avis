# BrewIQ · Flask API · app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=["http://localhost:3000"])

    Swagger(app, template={
        "info": {"title": "BrewIQ API", "version": "1.0", "description": "Coffee AI Platform REST API"},
        "securityDefinitions": {"Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}}
    })

    from app.routes.auth      import auth_bp
    from app.routes.sales     import sales_bp
    from app.routes.sentiment import sentiment_bp
    from app.routes.predict   import predict_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.products  import products_bp

    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(sales_bp,     url_prefix='/api/sales')
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(predict_bp,   url_prefix='/api/predictions')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(products_bp,  url_prefix='/api/products')

    return app
