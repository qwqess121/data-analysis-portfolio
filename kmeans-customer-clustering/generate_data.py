"""生成模拟电商交易数据，用于 K-Means 客户聚类（与 RFM 同源场景）。"""
import sqlite3
import random
import os
from datetime import date, timedelta

random.seed(99)
BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "transactions.db")
END = date(2025, 12, 31)


def generate():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE transactions (
            invoice_no TEXT,
            customer_id INTEGER,
            invoice_date TEXT,
            quantity INTEGER,
            unit_price REAL,
            country TEXT)"""
    )
    countries = ["中国", "美国", "英国", "德国", "日本", "法国", "加拿大", "澳大利亚"]
    rows, inv = [], 1
    for cid in range(1, 601):
        p = random.random()
        if p < 0.15:
            n, rec, spend = random.randint(15, 30), random.randint(1, 30), random.uniform(80, 300)
        elif p < 0.45:
            n, rec, spend = random.randint(8, 16), random.randint(10, 90), random.uniform(40, 150)
        elif p < 0.7:
            n, rec, spend = random.randint(4, 9), random.randint(30, 150), random.uniform(20, 90)
        else:
            n, rec, spend = random.randint(1, 4), random.randint(120, 360), random.uniform(10, 50)
        for _ in range(n):
            d = END - timedelta(days=max(1, rec + random.randint(-20, 60)))
            qty = random.randint(1, 5)
            price = round(spend * random.uniform(0.6, 1.4), 2)
            rows.append((f"INV{inv}", cid, d.isoformat(), qty, price, random.choice(countries)))
            inv += 1
    cur.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"已生成 {len(rows)} 条交易 -> {DB}")


if __name__ == "__main__":
    generate()
