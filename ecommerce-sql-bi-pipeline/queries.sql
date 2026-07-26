-- 电商 SQL+BI 分析：常用业务查询（SQLite）
-- 数据库：ecommerce.db

-- 1. 月度营收趋势
SELECT substr(o.order_date,1,7) AS month,
       SUM(oi.price + oi.freight) AS revenue,
       COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'delivered'
GROUP BY month ORDER BY month;

-- 2. 品类销售排行
SELECT p.category, SUM(oi.price + oi.freight) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'delivered'
GROUP BY p.category ORDER BY revenue DESC;

-- 3. 各州销售与物流时效
SELECT c.state,
       SUM(oi.price + oi.freight) AS revenue,
       ROUND(AVG(julianday(o.delivery_date) - julianday(o.order_date)),1) AS avg_delivery_days
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'delivered'
GROUP BY c.state ORDER BY revenue DESC;

-- 4. 客户复购分析
SELECT customer_id, COUNT(DISTINCT order_id) AS cnt
FROM orders WHERE status='delivered'
GROUP BY customer_id HAVING cnt > 1
ORDER BY cnt DESC;

-- 5. 取消订单率（按月）
SELECT substr(order_date,1,7) AS month,
       SUM(CASE WHEN status='canceled' THEN 1 ELSE 0 END) AS canceled,
       COUNT(*) AS total,
       ROUND(100.0*SUM(CASE WHEN status='canceled' THEN 1 ELSE 0 END)/COUNT(*),2) AS cancel_rate
FROM orders GROUP BY month ORDER BY month;
