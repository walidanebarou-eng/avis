-- BrewIQ · Coffee AI Platform · Database Schema
-- Compatible: PostgreSQL 14+ / MySQL 8+

CREATE DATABASE IF NOT EXISTS brewiq;
USE brewiq;

-- Users (JWT Auth)
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(80)  UNIQUE NOT NULL,
    email       VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role        ENUM('admin','manager','viewer') DEFAULT 'viewer',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    category    VARCHAR(50),
    base_price  DECIMAL(8,2),
    icon        VARCHAR(10),
    active      BOOLEAN DEFAULT TRUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sales
CREATE TABLE sales (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    product_id      INT NOT NULL,
    sale_date       DATE NOT NULL,
    sale_time       TIME,
    hour_of_day     TINYINT,
    time_of_day     ENUM('Morning','Afternoon','Night'),
    weekday         VARCHAR(10),
    weekday_sort    TINYINT,
    month_name      VARCHAR(10),
    month_sort      TINYINT,
    amount          DECIMAL(8,2) NOT NULL,
    cash_type       VARCHAR(20) DEFAULT 'card',
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Reviews
CREATE TABLE reviews (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    sale_id     INT,
    product_id  INT,
    review_text TEXT NOT NULL,
    sentiment   ENUM('positif','neutre','négatif'),
    sentiment_score DECIMAL(4,3),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id)    REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Predictions
CREATE TABLE predictions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    product_id      INT,
    target_month    DATE NOT NULL,
    predicted_rev   DECIMAL(10,2),
    predicted_cnt   INT,
    confidence      DECIMAL(4,3),
    model_version   VARCHAR(20),
    generated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Seed products
INSERT INTO products (name, category, base_price, icon) VALUES
('Latte',               'Hot',  35.50, '☕'),
('Americano with Milk', 'Hot',  30.59, '🥛'),
('Cappuccino',          'Hot',  35.88, '🫖'),
('Americano',           'Hot',  25.98, '⚡'),
('Hot Chocolate',       'Hot',  35.99, '🍫'),
('Cocoa',               'Hot',  35.65, '🍵'),
('Cortado',             'Hot',  25.73, '🥛'),
('Espresso',            'Hot',  20.85, '⚙️');

-- Seed admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@brewiq.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMaAkMIjXFDy6Fv0N8kXrHcMoe', 'admin');

CREATE INDEX idx_sales_date        ON sales(sale_date);
CREATE INDEX idx_sales_product     ON sales(product_id);
CREATE INDEX idx_sales_month       ON sales(month_sort);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment);
