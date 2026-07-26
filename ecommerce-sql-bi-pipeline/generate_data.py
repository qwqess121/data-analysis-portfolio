"""生成模拟巴西电商 (Olist 风格) 数据集，用于 SQL + BI 分析流水线。"""
import sqlite3
import random
import os
import numpy as np
from datetime import date, timedelta

random.seed(7)
np.random.seed(7)
BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "ecommerce.db")

STATES = ["SP", "RJ", "MG", "BA", "RS", "PR", "SC", "PE", "CE", "DF", "AM", "PA"]
CATEGORIES = ["电子产品", "家居家具", "美妆健康", "运动休闲", "服饰", "图书", "玩具", "电脑配件", "宠物用品", "厨具"]


def generate():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, state TEXT)")
    cur.execute(
        """CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            category TEXT,
            price REAL)"""
    )
    cur.execute(
        """CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            status TEXT,
            delivery_date TEXT)"""
    )
    cur.execute(
        """CREATE TABLE order_items (
            item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            price REAL,
            freight REAL)"""
    )

    # 客户
    customers = [(cid, random.choice(STATES)) for cid in range(1, 1001)]
    cur.executemany("INSERT INTO customers VALUES (?,?)", customers)

    # 产品
    products = [
        (pid, random.choice(CATEGORIES), round(random.uniform(20, 800), 2))
        for pid in range(1, 101)
    ]
    cur.executemany("INSERT INTO products VALUES (?,?,?)", products)

    start = date(2023, 1, 1)
    orders = []
    items = []
    oid = 1
    iid = 1
    n_customers = 10000
    # 季节性权重：业务增长 + 11/12月与5月旺季
    day_weights = []
    for d in range(730):
        day = start + timedelta(days=d)
        day_weights.append((1 + d / 730 * 0.8) * (1 + 0.5 * (day.month in (11, 12)) + 0.3 * (day.month == 5)))
    # 偏态分布：90% 客户仅 1 单，10% 为忠诚客户（多单），贴近真实电商留存结构
    for cid in range(1, n_customers + 1):
        n_orders = 1 if random.random() < 0.9 else random.randint(5, 80)
        for _ in range(n_orders):
            d = random.choices(range(730), weights=day_weights)[0]
            day = start + timedelta(days=d)
            odate = day.isoformat()
            canceled = random.random() < 0.08
            status = "canceled" if canceled else "delivered"
            ddate = (day + timedelta(days=random.randint(3, 25))).isoformat() if not canceled else None
            orders.append((oid, cid, odate, status, ddate))
            n_items = random.randint(1, 3)
            for _ in range(n_items):
                pid = random.randint(1, 100)
                price = round(random.uniform(20, 800), 2)
                freight = round(price * random.uniform(0.05, 0.2), 2)
                items.append((iid, oid, pid, price, freight))
                iid += 1
            oid += 1

    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", items)
    conn.commit()
    conn.close()
    print(f"已生成 {len(orders)} 笔订单、{len(items)} 条订单明细 -> {DB}")


if __name__ == "__main__":
    generate()
