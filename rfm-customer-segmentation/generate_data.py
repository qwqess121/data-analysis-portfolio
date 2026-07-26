"""生成模拟电商交易数据（Online Retail 风格），用于 RFM 客户分层。"""
import sqlite3
import random
import os
from datetime import date, timedelta

random.seed(2025)
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
    rows = []
    inv = 1
    # 为不同客户设定活跃度画像，使 RFM 分层有意义
    for cid in range(1, 501):
        profile = random.random()
        if profile < 0.18:       # 高价值：近期、高频、高客单
            n = random.randint(15, 30)
            recency_day = random.randint(1, 30)
            spend = random.uniform(80, 300)
        elif profile < 0.45:     # 忠诚：中高频
            n = random.randint(8, 16)
            recency_day = random.randint(10, 90)
            spend = random.uniform(40, 150)
        elif profile < 0.7:      # 潜力
            n = random.randint(4, 9)
            recency_day = random.randint(30, 150)
            spend = random.uniform(20, 90)
        else:                    # 沉睡/低价值
            n = random.randint(1, 4)
            recency_day = random.randint(120, 360)
            spend = random.uniform(10, 50)
        for _ in range(n):
            days_ago = max(1, recency_day + random.randint(-20, 60))
            d = END - timedelta(days=days_ago)
            qty = random.randint(1, 5)
            price = round(spend * random.uniform(0.6, 1.4), 2)
            rows.append((f"INV{inv}", cid, d.isoformat(), qty, price, random.choice(countries)))
            inv += 1
    cur.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"已生成 {len(rows)} 条交易记录 -> {DB}")


if __name__ == "__main__":
    generate()
