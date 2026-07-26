import sqlite3
import pandas as pd
import streamlit as st

DB = "ecommerce.db"


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(
        """
        SELECT o.order_id, o.customer_id, o.product_id, o.quantity, o.order_date, o.country,
               p.name AS product_name, p.category, p.price,
               o.quantity * p.price AS revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        """,
        conn,
    )
    conn.close()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def main():
    st.set_page_config(page_title="电商销售分析看板", layout="wide")
    st.title("📊 电商销售分析看板")

    df = load_data()
    total_rev = df["revenue"].sum()
    total_orders = df["order_id"].nunique()
    top_product = df.groupby("product_name")["revenue"].sum().idxmax()
    active_customers = df["customer_id"].nunique()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("总营收", f"¥{total_rev:,.0f}")
    k2.metric("订单数", f"{total_orders:,}")
    k3.metric("活跃客户", f"{active_customers:,}")
    k4.metric("最畅销产品", top_product)

    st.subheader("月度营收趋势")
    monthly = df.groupby("month")["revenue"].sum().reset_index()
    st.line_chart(monthly.set_index("month"))

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("品类销售")
        st.bar_chart(df.groupby("category")["revenue"].sum().sort_values(ascending=False))
    with c2:
        st.subheader("国家/地区销售 Top10")
        cty = df.groupby("country")["revenue"].sum().sort_values(ascending=False).head(10)
        st.bar_chart(cty)

    st.subheader("Top 10 产品")
    top = df.groupby("product_name")["revenue"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top)

    st.subheader("原始数据预览")
    st.dataframe(df.head(100))


if __name__ == "__main__":
    main()
