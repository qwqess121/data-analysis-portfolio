"""生成供应链需求数据（含季节性），用于需求预测与补货优化。"""
import sqlite3
import random
import math
import os
from datetime import date, timedelta

random.seed(31)
BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "supply_chain.db")
START = date(2024, 1, 1)
N_DAYS = 540


def generate():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE demand (
            date TEXT,
            product_id INTEGER,
            demand INTEGER,
            inventory INTEGER,
            price REAL)"""
    )
    rows = []
    for pid in range(1, 21):
        base = random.uniform(20, 80)
        amp = base * random.uniform(0.2, 0.5)
        phase = random.uniform(0, 2 * math.pi)
        inv = random.randint(50, 300)
        for d in range(N_DAYS):
            day = START + timedelta(days=d)
            trend = 1 + d / N_DAYS * 0.3
            seasonal = 1 + (amp / base) * math.sin(2 * math.pi * d / 365 + phase)
            weekly = 1 + 0.15 * (day.weekday() >= 5)
            noise = random.gauss(1, 0.12)
            dem = max(0, int(base * trend * seasonal * weekly * noise))
            inv = max(0, inv - dem + random.randint(0, 40))
            rows.append((day.isoformat(), pid, dem, inv, round(base * 3, 2)))
    cur.executemany("INSERT INTO demand VALUES (?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"已生成 {len(rows)} 条供需记录 -> {DB}")


if __name__ == "__main__":
    generate()
