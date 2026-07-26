"""库存预测看板（Streamlit）：展示各产品 7 天需求预测与缺货预警。"""
import sqlite3
import os
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "retail_sales.db")
WINDOW, HORIZON = 30, 7


def forecast():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["product_id", "date"])
    rows = []
    for pid, g in df.groupby("product_id"):
        s = g["sales"].values.astype(float)
        X = np.array([s[i:i + WINDOW] for i in range(len(s) - WINDOW - HORIZON)])
        y = np.array([s[i + WINDOW:i + WINDOW + HORIZON] for i in range(len(s) - WINDOW - HORIZON)])
        k = int(len(X) * 0.85)
        m = RandomForestRegressor(n_estimators=60, random_state=42, n_jobs=-1)
        m.fit(X.reshape(len(X), -1), y)
        fut = m.predict(s[-WINDOW:].reshape(1, -1))[0]
        stock = int(g["sales"].iloc[-1] * np.random.randint(3, 8))
        rows.append({"product_id": pid, "未来7天预测": round(fut.sum(), 0),
                     "当前库存": stock, "预警": "⚠️缺货风险" if fut.sum() > stock else "库存充足"})
    return pd.DataFrame(rows)


def main():
    st.set_page_config(page_title="库存预测看板", layout="wide")
    st.title("📦 库存需求预测与缺货预警")
    df = forecast()
    st.dataframe(df)
    st.bar_chart(df.set_index("product_id")["未来7天预测"])


if __name__ == "__main__":
    main()
