"""电商 SQL + BI 分析：连接 SQLite，执行业务分析 SQL，导出 Power BI 可用数据集。"""
import sqlite3
import os
import pandas as pd

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "ecommerce.db")
OUT = os.path.join(BASE, "outputs")
os.makedirs(OUT, exist_ok=True)


def run():
    conn = sqlite3.connect(DB)

    # 1. 月度营收趋势
    monthly = pd.read_sql_query(
        """
        SELECT substr(o.order_date,1,7) AS month,
               SUM(oi.price + oi.freight) AS revenue,
               COUNT(DISTINCT o.order_id) AS orders
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'delivered'
        GROUP BY month ORDER BY month
        """,
        conn,
    )

    # 2. 品类销售
    category = pd.read_sql_query(
        """
        SELECT p.category,
               SUM(oi.price + oi.freight) AS revenue,
               SUM(oi.price) AS product_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.status = 'delivered'
        GROUP BY p.category ORDER BY revenue DESC
        """,
        conn,
    )

    # 3. 各州销售与物流时效
    state = pd.read_sql_query(
        """
        SELECT c.state,
               SUM(oi.price + oi.freight) AS revenue,
               COUNT(DISTINCT o.order_id) AS orders,
               ROUND(AVG(julianday(o.delivery_date) - julianday(o.order_date)),1) AS avg_delivery_days
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status = 'delivered'
        GROUP BY c.state ORDER BY revenue DESC
        """,
        conn,
    )

    # 4. 客户留存（重复购买比例）
    retention = pd.read_sql_query(
        """
        SELECT COUNT(*) AS total_customers,
               SUM(CASE WHEN cnt > 1 THEN 1 ELSE 0 END) AS repeat_customers
        FROM (
            SELECT customer_id, COUNT(DISTINCT order_id) AS cnt
            FROM orders WHERE status='delivered'
            GROUP BY customer_id
        )
        """,
        conn,
    )

    # 5. 取消订单分析
    cancel = pd.read_sql_query(
        """
        SELECT substr(order_date,1,7) AS month,
               SUM(CASE WHEN status='canceled' THEN 1 ELSE 0 END) AS canceled,
               COUNT(*) AS total,
               ROUND(100.0*SUM(CASE WHEN status='canceled' THEN 1 ELSE 0 END)/COUNT(*),2) AS cancel_rate
        FROM orders GROUP BY month ORDER BY month
        """,
        conn,
    )

    # 订单明细宽表（供 Power BI 建模）
    detail = pd.read_sql_query(
        """
        SELECT o.order_id, o.customer_id, c.state, o.order_date, o.status,
               p.category, oi.price, oi.freight, (oi.price+oi.freight) AS total
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN customers c ON o.customer_id = c.customer_id
        """,
        conn,
    )

    conn.close()

    monthly.to_csv(os.path.join(OUT, "monthly_revenue.csv"), index=False)
    category.to_csv(os.path.join(OUT, "category_sales.csv"), index=False)
    state.to_csv(os.path.join(OUT, "state_sales.csv"), index=False)
    retention.to_csv(os.path.join(OUT, "retention.csv"), index=False)
    cancel.to_csv(os.path.join(OUT, "cancellation.csv"), index=False)
    detail.to_csv(os.path.join(OUT, "order_detail.csv"), index=False)

    rep_rate = retention.iloc[0]["repeat_customers"] / retention.iloc[0]["total_customers"]
    print("=== 业务洞察 ===")
    print(f"总营收: ¥{monthly['revenue'].sum():,.0f}")
    print(f"Top 州: {state.iloc[0]['state']} (¥{state.iloc[0]['revenue']:,.0f})")
    print(f"复购客户占比: {rep_rate*100:.1f}%")
    print(f"平均物流时效: {state['avg_delivery_days'].mean():.1f} 天")
    print(f"整体取消率: {cancel['canceled'].sum()/cancel['total'].sum()*100:.1f}%")
    print(f"输出文件已保存到 outputs/")


if __name__ == "__main__":
    run()
