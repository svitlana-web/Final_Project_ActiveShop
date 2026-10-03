-- ActiveShop Database Schema Creation Script (Updated Key Types to VARCHAR)

DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- 1. Table: customers
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    signup_date DATE NOT NULL,
    age NUMERIC(5, 1),
    gender VARCHAR(20),
    city VARCHAR(100),
    region VARCHAR(100),
    acquisition_channel VARCHAR(50),
    loyalty_level VARCHAR(50),
    ab_group VARCHAR(10)
);

-- 2. Table: products
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    unit_cost NUMERIC(10, 2) NOT NULL,
    list_price NUMERIC(10, 2) NOT NULL
);

-- 3. Table: orders
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    shipping_type VARCHAR(50),
    promo_code VARCHAR(50),
    discount_percent NUMERIC(5, 2),
    gross_amount NUMERIC(12, 2),
    order_amount NUMERIC(12, 2),
    delivery_days NUMERIC(5, 1),
    customer_rating NUMERIC(3, 1)
);

-- 4. Table: sessions
CREATE TABLE sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    session_start TIMESTAMP NOT NULL,
    channel VARCHAR(50),
    device VARCHAR(50),
    ab_group VARCHAR(10),
    converted INT CHECK (converted IN (0, 1)),
    order_id VARCHAR(50) REFERENCES orders(order_id) ON DELETE SET NULL
);

-- 5. Table: order_items
CREATE TABLE order_items (
    item_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL,
    line_amount NUMERIC(12, 2) NOT NULL
);