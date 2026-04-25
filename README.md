# BrewIQ — AI Coffee Sales Intelligence Platform

**Stack:** Flask · React.js · MySQL · Random Forest · NLP FR · JWT · Docker · Swagger

---

## Architecture

```
brewiq/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask factory + extensions
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── routes/
│   │       └── routes.py        # auth / sales / sentiment / predict / dashboard / products
│   ├── ml/
│   │   ├── sentiment.py         # NLP FR: règles lexicales + TextBlob fallback
│   │   └── predictor.py         # Random Forest training + forecasting
│   ├── utils/
│   │   └── data_loader.py       # CSV loader + aggregations
│   ├── config.py
│   ├── run.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx              # Shell + routing
│       ├── App.css              # Design system complet
│       ├── hooks/
│       │   └── useAuth.jsx      # AuthContext + useApi + apiPost
│       └── pages/
│           ├── Dashboard.jsx    # KPIs + graphiques mensuels
│           ├── Analytics.jsx    # Analyse produit/jour/heure
│           ├── SentimentPage.jsx# NLP live + distribution
│           ├── PredictPage.jsx  # Prévisions RF 2025
│           ├── ProductsPage.jsx # Catalogue produits
│           └── StocksPage.jsx   # Gestion stocks
├── database/
│   └── schema.sql               # MySQL schema + seeds
├── docker/
│   └── Dockerfile.backend
├── docker-compose.yml
└── README.md
```

---

## Dataset

| Colonne        | Type    | Description                  |
|----------------|---------|------------------------------|
| hour_of_day    | int     | Heure (6–22)                 |
| cash_type      | str     | Mode de paiement             |
| money          | float   | Montant (€)                  |
| coffee_name    | str     | Nom du produit (8 types)     |
| Time_of_Day    | str     | Morning / Afternoon / Night  |
| Weekday        | str     | Lun–Dim                      |
| Month_name     | str     | Jan–Déc                      |
| Date           | str     | Date de vente                |
| customer_review| str     | Avis client (FR)             |

**3 547 transactions · 8 produits · 12 mois · 12 avis uniques**

---

## API REST

| Méthode | Endpoint                        | Description                        |
|---------|---------------------------------|------------------------------------|
| POST    | `/api/auth/login`               | Connexion → JWT token              |
| POST    | `/api/auth/register`            | Création compte                    |
| GET     | `/api/dashboard/`               | Tous les KPIs en un seul appel     |
| GET     | `/api/sales/?group_by=product`  | Ventes groupées (product/month/…)  |
| GET     | `/api/sales/top-products`       | Top N produits                     |
| GET     | `/api/sentiment/`               | Analyse NLP de tous les avis       |
| POST    | `/api/sentiment/analyse`        | Analyser un avis en temps réel     |
| GET     | `/api/predictions/`             | Prévisions mensuelles RF 2025      |
| GET     | `/api/predictions/by-product`   | Prévisions par produit             |
| GET     | `/api/predictions/popular`      | Produits populaires par moment     |
| POST    | `/api/predictions/train`        | Re-entraîner le modèle (admin)     |
| GET     | `/api/products/`                | Catalogue + KPIs                   |

**Swagger UI:** `http://localhost:5000/apidocs`

---

## Installation rapide

### Option A — Docker (recommandé)

```bash
git clone https://github.com/yourorg/brewiq
cd brewiq

# Copier le CSV dans data/
cp Coffe_sales_with_reviews.csv data/

docker-compose up --build
```

- Frontend : http://localhost:3000
- Backend  : http://localhost:5000
- Swagger  : http://localhost:5000/apidocs

**Credentials par défaut :** `admin` / `admin123`

---

### Option B — Développement local

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Config
cp .env.example .env
# Éditer DATABASE_URL, SECRET_KEY, CSV_PATH

# MySQL
mysql -u root -p < ../database/schema.sql

python run.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Modèles IA

### Sentiment NLP (FR)
- Règles lexicales sur dictionnaire positif/négatif FR
- Détection de phrases inversives (« pas cher », « trop coûteux »)
- Score continu [-1, +1] + label + confidence
- Résultat : **78% positifs**, 17% neutres, 8% négatifs

### Prédiction (Random Forest)
```
Features: month_sort, weekday_sort, hour_of_day, product_enc, time_enc
Target:   money (€ par transaction)
```
- 200 estimateurs, profondeur max 8, 80/20 train/test
- Forecasting 2025 = base 2024 × 1.08 + décomposition saisonnière
- Re-entraînement via `POST /api/predictions/train`

---

## Export PDF

```python
# backend/utils/report.py (à intégrer)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

def generate_report(data: dict, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    # Build PDF with KPIs, charts, sentiment summary
    doc.build([...])
```

Endpoint : `GET /api/dashboard/export-pdf` → retourne le PDF.

---

## Variables d'environnement

| Variable       | Défaut                             | Description            |
|----------------|------------------------------------|------------------------|
| DATABASE_URL   | mysql+pymysql://root:pw@localhost/brewiq | Connexion MySQL  |
| SECRET_KEY     | —                                  | Flask secret key       |
| JWT_SECRET_KEY | —                                  | JWT signing key        |
| CSV_PATH       | data/Coffe_sales_with_reviews.csv  | Chemin du dataset      |
| PORT           | 5000                               | Port Flask             |

---

## Sécurité

- Authentification JWT (8h d'expiration)
- Mots de passe hashés Werkzeug (bcrypt)
- CORS limité à `localhost:3000`
- Routes protégées par `@jwt_required()`
- Rôles : `admin`, `manager`, `viewer`
