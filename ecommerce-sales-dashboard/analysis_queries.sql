-- 电商销售分析：常用 SQL 查询示例
-- 数据库：ecommerce.db (SQLite)

-- 1. 月度营收趋势
SELECT substr(order_date, 1, 7) AS month,
       SUM(o.quantity * p.price) AS revenue,
       COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY month
ORDER BY month;

-- 2. 各品类销售额
SELECT p.category,
       SUM(o.quantity * p.price) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 3. Top 10 最畅销产品
SELECT p.name,
       SUM(o.quantity) AS total_qty,
       SUM(o.quantity * p.price) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 10;

-- 4. 各国营收 + 客户数
SELECT o.country,
       SUM(o.quantity * p.price) AS revenue,
       COUNT(DISTINCT o.customer_id) AS customers
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY o.country
ORDER BY revenue DESC;

-- 5. 客户购买频次排名（RF 维度）
SELECT o.customer_id,
       COUNT(DISTINCT o.order_id) AS frequency,
       SUM(o.quantity * p.price) AS monetary
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY o.customer_id
ORDER BY monetary DESC
LIMIT 20;
