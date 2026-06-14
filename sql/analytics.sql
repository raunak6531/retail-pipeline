-- ============================================================
-- RETAIL SALES ANALYTICS QUERIES
-- Run against: data/retail.db  (table: sales)
-- ============================================================


-- 1. Total revenue, orders, and return rate overview
SELECT
    COUNT(transaction_id)                        AS total_orders,
    ROUND(SUM(net_revenue), 2)                   AS total_net_revenue,
    ROUND(AVG(net_revenue), 2)                   AS avg_order_value,
    ROUND(SUM(CASE WHEN is_returned = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM sales;


-- 2. Monthly revenue trend
SELECT
    year,
    month,
    ROUND(SUM(net_revenue), 2) AS monthly_revenue,
    COUNT(transaction_id)      AS total_orders
FROM sales
WHERE net_revenue > 0
GROUP BY year, month
ORDER BY year, month;


-- 3. Top 5 categories by net revenue
SELECT
    category,
    ROUND(SUM(net_revenue), 2) AS total_revenue,
    COUNT(transaction_id)      AS total_orders,
    ROUND(AVG(discount_pct) * 100, 2) AS avg_discount_pct
FROM sales
WHERE net_revenue > 0
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 5;


-- 4. Regional performance comparison
SELECT
    region,
    ROUND(SUM(net_revenue), 2)                              AS total_revenue,
    COUNT(transaction_id)                                   AS total_orders,
    ROUND(SUM(CASE WHEN is_returned=1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;


-- 5. Top 10 products by units sold
SELECT
    product_name,
    category,
    SUM(quantity)              AS units_sold,
    ROUND(SUM(net_revenue), 2) AS total_revenue
FROM sales
WHERE net_revenue > 0
GROUP BY product_name, category
ORDER BY units_sold DESC
LIMIT 10;


-- 6. Payment method distribution
SELECT
    payment_method,
    COUNT(*)                                          AS num_transactions,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales), 2) AS pct_share
FROM sales
GROUP BY payment_method
ORDER BY num_transactions DESC;


-- 7. Weekend vs weekday sales
SELECT
    CASE WHEN weekday IN ('Saturday', 'Sunday') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(transaction_id)      AS total_orders,
    ROUND(SUM(net_revenue), 2) AS total_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_order_value
FROM sales
WHERE net_revenue > 0
GROUP BY day_type;


-- 8. High-value customers segment (Premium revenue bucket)
SELECT
    revenue_bucket,
    COUNT(*)                   AS num_transactions,
    ROUND(SUM(net_revenue), 2) AS total_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_order_value
FROM sales
WHERE net_revenue > 0
GROUP BY revenue_bucket
ORDER BY avg_order_value DESC;
