-- ===================================================================
-- E-Commerce Analytics: ActiveShop Project
-- Phase 2: PostgreSQL SQL Analytical Queries (Executed in DBeaver)
-- ===================================================================
-- ----------------------------------------------------------------------------
-- 1. CORE BUSINESS METRICS
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(order_id) AS successful_orders_count,
    ROUND(SUM(order_amount), 2) AS total_revenue,
    ROUND(AVG(order_amount), 2) AS average_order_value,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY order_amount)::numeric, 2) AS median_order_value,
    COUNT(DISTINCT customer_id) AS unique_buyers_count
FROM orders
WHERE LOWER(status) = 'delivered';

-- ----------------------------------------------------------------------------
-- 2. SALES DYNAMICS BY MONTH (WITH LAG)
-- ----------------------------------------------------------------------------
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date)::DATE AS order_month,
        COUNT(order_id) AS orders_count,
        ROUND(SUM(order_amount), 2) AS total_revenue,
        ROUND(AVG(order_amount), 2) AS average_order_value
    FROM orders
    WHERE LOWER(status) = 'delivered'
    GROUP BY DATE_TRUNC('month', order_date)::DATE
)
SELECT 
    order_month,
    orders_count,
    total_revenue,
    average_order_value,
    LAG(total_revenue) OVER (ORDER BY order_month) AS prev_month_revenue,
    ROUND(
        (total_revenue - LAG(total_revenue) OVER (ORDER BY order_month)) 
        / LAG(total_revenue) OVER (ORDER BY order_month) * 100, 2
    ) AS revenue_growth_pct
FROM monthly_sales
ORDER BY order_month;

-- ----------------------------------------------------------------------------
-- 3. CATEGORY & PRODUCT PERFORMANCE (NET REVENUE & GROSS PROFIT)
-- ----------------------------------------------------------------------------

-- Gross Profit = net_revenue - (unit_cost * quantity)
SELECT 
    p.category,
    ROUND(SUM(oi.line_amount * (1 - COALESCE(o.discount_percent, 0) / 100.0)), 2) AS net_revenue,
    ROUND(SUM(oi.line_amount * (1 - COALESCE(o.discount_percent, 0) / 100.0) - (p.unit_cost * oi.quantity)), 2) AS gross_profit
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE LOWER(o.status) = 'delivered'
GROUP BY p.category
ORDER BY net_revenue DESC;

--  Top-5 products by revenue
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(oi.line_amount * (1 - COALESCE(o.discount_percent, 0) / 100.0)), 2) AS net_revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE LOWER(o.status) = 'delivered'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY net_revenue DESC
LIMIT 5;

--  Top-5 products by units sold
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_units_sold
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE LOWER(o.status) = 'delivered'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_units_sold DESC
LIMIT 5;

-- ----------------------------------------------------------------------------
-- 4. PRODUCT RANKING WITHIN CATEGORIES (TOP-3 BY REVENUE)
-- ----------------------------------------------------------------------------
WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        ROUND(SUM(oi.line_amount * (1 - COALESCE(o.discount_percent, 0) / 100.0)), 2) AS net_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE LOWER(o.status) = 'delivered'
    GROUP BY p.category, p.product_id, p.product_name
),
ranked_products AS (
    SELECT 
        category,
        product_id,
        product_name,
        net_revenue,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY net_revenue DESC) AS category_rank
    FROM product_revenue
)
SELECT 
    category,
    category_rank,
    product_name,
    product_id,
    net_revenue
FROM ranked_products
WHERE category_rank <= 3
ORDER BY category, category_rank;


-- ----------------------------------------------------------------------------
-- 5. CUSTOMERS AND RETENTION
-- ----------------------------------------------------------------------------

-- 5.1 Top-10 customers by revenue
SELECT 
    c.customer_id,
    c.city,
    c.loyalty_level,
    SUM(o.order_amount) AS total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE LOWER(o.status) = 'delivered'
GROUP BY c.customer_id, c.city, c.loyalty_level
ORDER BY total_revenue DESC
LIMIT 10;

-- 5.2 Customers with highest number of successful orders
SELECT 
    c.customer_id,
    c.loyalty_level,
    COUNT(o.order_id) AS successful_orders_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE LOWER(o.status) = 'delivered'
GROUP BY c.customer_id, c.loyalty_level
ORDER BY successful_orders_count DESC
LIMIT 10;

-- 5.3 Repeat customer rate (share of customers with > 1 successful order)
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        COUNT(CASE WHEN LOWER(o.status) = 'delivered' THEN o.order_id END) AS successful_orders
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
)
SELECT 
    COUNT(CASE WHEN successful_orders > 1 THEN 1 END) AS repeat_customers_count,
    COUNT(CASE WHEN successful_orders >= 1 THEN 1 END) AS total_buying_customers,
    ROUND(
        COUNT(CASE WHEN successful_orders > 1 THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(CASE WHEN successful_orders >= 1 THEN 1 END), 0) * 100, 
        2
    ) AS repeat_customer_share_pct
FROM customer_orders;


-- ----------------------------------------------------------------------------
-- 6. MARKETING CHANNELS (SESSIONS FUNNEL & REVENUE)
-- ----------------------------------------------------------------------------
SELECT 
    s.channel,
    COUNT(s.session_id) AS total_sessions,
    SUM(s.converted) AS converted_orders_count,
    ROUND(
        SUM(s.converted)::NUMERIC / COUNT(s.session_id) * 100, 
        2
    ) AS conversion_rate_pct,
    COALESCE(SUM(o.order_amount), 0) AS total_channel_revenue
FROM sessions s
LEFT JOIN orders o ON s.order_id = o.order_id AND LOWER(o.status) = 'delivered'
GROUP BY s.channel
ORDER BY total_channel_revenue DESC;



-- ----------------------------------------------------------------------------
-- 7. PROMO CODE IMPACT ANALYSIS (Handling 'NONE' values)
-- ----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN promo_code IS NOT NULL 
         AND UPPER(TRIM(promo_code)) NOT IN ('', 'NONE', 'NULL') 
        THEN 'With Promo Code'
        ELSE 'Without Promo Code'
    END AS promo_status,
    COUNT(order_id) AS orders_count,
    ROUND(AVG(order_amount), 2) AS average_order_value,
    ROUND(SUM(order_amount), 2) AS total_revenue
FROM orders
WHERE LOWER(status) = 'delivered'
GROUP BY 
    CASE 
        WHEN promo_code IS NOT NULL 
         AND UPPER(TRIM(promo_code)) NOT IN ('', 'NONE', 'NULL') 
        THEN 'With Promo Code'
        ELSE 'Without Promo Code'
    END;

-- ----------------------------------------------------------------------------
-- 8. ANALYTICAL VIEW CREATION
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_order_analytics AS
SELECT 
    o.order_id,
    o.order_date,
    DATE_TRUNC('month', o.order_date)::DATE AS order_month,
    o.status AS order_status,
    o.order_amount,
    o.discount_percent,
    o.promo_code,
    o.payment_method,
    c.customer_id,
    c.city AS customer_city,
    c.region AS customer_region,
    c.loyalty_level,
    c.acquisition_channel AS customer_acquisition_channel,
    s.channel AS session_channel,
    s.device AS session_device
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN sessions s ON o.order_id = s.order_id
WHERE LOWER(o.status) = 'delivered';