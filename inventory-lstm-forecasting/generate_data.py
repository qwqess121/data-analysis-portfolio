"""生成零售日度销量时序数据（M5 风格），用于库存 LSTM 预测。"""
import sqlite3
import random
import math
import os
from datetime import date, timedelta

random.seed(123)
BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "retail_sales.db")
START = date(2022, 1, 1)
N_DAYS = 1095


def generate():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE sales (date TEXT, product_id INTEGER, sales INTEGER, price REAL)")
    rows = []
    for pid in range(1, 11):
        base = random.uniform(30, 120)
        phase = random.uniform(0, 2 * math.pi)
        for d in range(N_DAYS):
            day = START + timedelta(days=d)
            trend = 1 + d / N_DAYS * 0.4
            season = 1 + 0.3 * math.sin(2 * math.pi * d / 365 + phase)
            promo = 1.6 if random.random() < 0.05 else 1.0
            weekly = 1 + 0.2 * (day.weekday() >= 5)
            noise = random.gauss(1, 0.15)
            s = max(0, int(base * trend * season * promo * weekly * noise))
            rows.append((day.isoformat(), pid, s, round(base * 4, 2)))
    cur.executemany("INSERT INTO sales VALUES (?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"已生成 {len(rows)} 条日度销量 -> {DB}")


if __name__ == "__main__":
    generate()
