# BrewIQ · app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint
    ---
    parameters:
      - in: body
        schema:
          properties:
            username: {type: string}
            password: {type: string}
    responses:
      200:
        description: JWT token
    """
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password', '')):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = create_access_token(identity={'id': user.id, 'role': user.role})
    return jsonify({'access_token': token, 'role': user.role, 'username': user.username})

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201


# ── app/routes/sales.py ──────────────────────────────────────────────────────
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.data_loader import get_df, by_product, by_month, by_weekday, by_hour, by_time_of_day

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/', methods=['GET'])
@jwt_required()
def sales():
    """
    Sales data
    ---
    security:
      - Bearer: []
    parameters:
      - name: group_by
        in: query
        type: string
        enum: [product, month, weekday, hour, time_of_day]
    responses:
      200:
        description: Sales data grouped by dimension
    """
    group_by = request.args.get('group_by', 'product')
    df = get_df()
    dispatch = {
        'product':     by_product,
        'month':       by_month,
        'weekday':     by_weekday,
        'hour':        by_hour,
        'time_of_day': by_time_of_day,
    }
    fn = dispatch.get(group_by)
    if fn is None:
        return jsonify({'error': f'group_by must be one of: {list(dispatch.keys())}'}), 400
    return jsonify({'group_by': group_by, 'data': fn(df)})

@sales_bp.route('/top-products', methods=['GET'])
@jwt_required()
def top_products():
    df = get_df()
    limit = int(request.args.get('limit', 5))
    data = by_product(df)[:limit]
    return jsonify({'data': data})


# ── app/routes/sentiment.py ──────────────────────────────────────────────────
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ml.sentiment import analyse_sentiment, analyse_batch, sentiment_stats
from utils.data_loader import get_df

sentiment_bp = Blueprint('sentiment', __name__)

@sentiment_bp.route('/', methods=['GET'])
@jwt_required()
def get_sentiment():
    """
    Sentiment analysis on all reviews
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Sentiment analysis results
    """
    df = get_df()
    reviews = df['customer_review'].dropna().tolist()
    stats = sentiment_stats(reviews)
    sample = analyse_batch(list(set(reviews)))   # unique reviews
    return jsonify({'stats': stats, 'reviews': sample})

@sentiment_bp.route('/analyse', methods=['POST'])
@jwt_required()
def analyse_text():
    """
    Analyse a single review
    ---
    security:
      - Bearer: []
    parameters:
      - in: body
        schema:
          properties:
            text: {type: string}
    responses:
      200:
        description: Sentiment result
    """
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'text is required'}), 400
    result = analyse_sentiment(text)
    return jsonify({
        'text': text,
        'sentiment': result.label,
        'score': result.score,
        'confidence': result.confidence,
        'keywords': result.keywords
    })


# ── app/routes/predict.py ────────────────────────────────────────────────────
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ml.predictor import predict_monthly, predict_by_product, get_popular_products, train_model
from flask import current_app

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/', methods=['GET'])
@jwt_required()
def predictions():
    """
    Monthly revenue predictions
    ---
    security:
      - Bearer: []
    parameters:
      - name: months
        in: query
        type: integer
        default: 6
    responses:
      200:
        description: Monthly predictions for 2025
    """
    months = int(request.args.get('months', 6))
    csv = current_app.config['CSV_PATH']
    data = predict_monthly(csv, months)
    return jsonify({'model': 'RandomForest+Seasonality', 'predictions': data})

@predict_bp.route('/by-product', methods=['GET'])
@jwt_required()
def by_product_pred():
    csv = current_app.config['CSV_PATH']
    data = predict_by_product(csv)
    return jsonify({'data': data})

@predict_bp.route('/popular', methods=['GET'])
@jwt_required()
def popular():
    csv = current_app.config['CSV_PATH']
    data = get_popular_products(csv)
    return jsonify({'data': data})

@predict_bp.route('/train', methods=['POST'])
@jwt_required()
def train():
    """Trigger model retraining (admin only)."""
    csv = current_app.config['CSV_PATH']
    result = train_model(csv)
    return jsonify(result)


# ── app/routes/dashboard.py ──────────────────────────────────────────────────
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.data_loader import get_df, sales_summary, by_product, by_month, by_time_of_day
from ml.sentiment import sentiment_stats

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def dashboard():
    """
    Global dashboard stats
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: All KPIs and chart data in one call
    """
    df = get_df()
    reviews = df['customer_review'].dropna().tolist()
    return jsonify({
        'kpis':        sales_summary(df),
        'by_product':  by_product(df),
        'by_month':    by_month(df),
        'by_tod':      by_time_of_day(df),
        'sentiment':   sentiment_stats(reviews),
    })


# ── app/routes/products.py ───────────────────────────────────────────────────
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from utils.data_loader import get_df

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
@jwt_required()
def products():
    """
    Product catalog with performance metrics
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Product list with KPIs
    """
    df = get_df()
    g = df.groupby('coffee_name').agg(
        revenue=('money', 'sum'),
        orders=('money', 'count'),
        avg_price=('money', 'mean')
    ).reset_index()
    g['revenue']   = g['revenue'].round(2)
    g['avg_price'] = g['avg_price'].round(2)
    return jsonify({'products': g.to_dict(orient='records')})
