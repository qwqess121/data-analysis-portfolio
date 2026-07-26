import sqlite3
import random
import os
import numpy as np
from datetime import date, timedelta

random.seed(42)
np.random.seed(42)
DB = os.path.join(os.path.dirname(__file__), "ecommerce.db")


def generate():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT)"""
    )
    cur.execute(
        """CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL)"""
    )
    cur.execute(
        """CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date TEXT,
            country TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id))"""
    )

    countries = ["中国", "美国", "英国", "德国", "日本", "法国", "加拿大", "澳大利亚", "巴西", "印度"]
    categories = ["电子产品", "服装", "家居", "美妆", "运动", "图书", "玩具"]
    products = []
    for pid in range(1, 51):
        cat = random.choice(categories)
        price = round(random.uniform(5, 500), 2)
        products.append((pid, f"{cat}商品{pid}", cat, price))
    cur.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

    customers = [(cid, f"客户{cid}", random.choice(countries)) for cid in range(1, 201)]
    cur.executemany("INSERT INTO customers VALUES (?,?,?)", customers)

    start = date(2025, 1, 1)
    orders = []
    oid = 1
    for d in range(365):
        day = start + timedelta(days=d)
        season = 1 + 0.6 * (day.month in (11, 12)) + 0.2 * (day.month in (6, 7))
        for _ in range(int(np.random.poisson(8 * season))):
            cid = random.randint(1, 200)
            pid = random.randint(1, 50)
            qty = random.randint(1, 5)
            orders.append((oid, cid, pid, qty, day.isoformat(), random.choice(countries)))
            oid += 1
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", orders)
    conn.commit()
    conn.close()
    print(f"已生成 {len(orders)} 条订单 -> {DB}")


if __name__ == "__main__":
    generate()
