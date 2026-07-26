"""生成模拟亚马逊竞品数据（BSR/价格/评论/评分），用于竞品分析。"""
import sqlite3
import random
import os
from datetime import date, timedelta

random.seed(888)
BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "competitor.db")
START = date(2025, 4, 1)
N_DAYS = 90
ASINS = {
    "B0A1": "竞品A-无线耳机",
    "B0B2": "竞品B-无线耳机",
    "B0C3": "竞品C-无线耳机",
    "B0D4": "竞品D-蓝牙音箱",
    "B0E5": "竞品E-蓝牙音箱",
}


def generate():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE listings (date TEXT, asin TEXT, name TEXT, bsr INTEGER, price REAL, reviews INTEGER, rating REAL)")
    rows = []
    for asin, name in ASINS.items():
        bsr = random.randint(200, 2000)
        price = round(random.uniform(20, 80), 2)
        reviews = random.randint(500, 3000)
        rating = round(random.uniform(4.0, 4.7), 2)
        for d in range(N_DAYS):
            day = START + timedelta(days=d)
            bsr = max(50, int(bsr * random.uniform(0.97, 1.03)))
            price = round(max(15, price * random.uniform(0.98, 1.03)), 2)
            reviews += random.randint(0, 15)
            rating = round(min(5.0, max(3.5, rating + random.gauss(0, 0.02))), 2)
            rows.append((day.isoformat(), asin, name, bsr, price, reviews, rating))
    cur.executemany("INSERT INTO listings VALUES (?,?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"已生成 {len(rows)} 条竞品数据 -> {DB}")


if __name__ == "__main__":
    generate()
