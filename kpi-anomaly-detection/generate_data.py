"""生成业务 KPI 日度数据（含异常注入），用于异常检测演示。"""
import sqlite3
import random
import os
from datetime import date, timedelta

random.seed(55)
BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "kpi.db")
START = date(2024, 1, 1)
N_DAYS = 540


def generate():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE kpi (date TEXT, revenue REAL, orders INTEGER, traffic INTEGER)")
    rows = []
    for d in range(N_DAYS):
        day = START + timedelta(days=d)
        trend = 1 + d / N_DAYS * 0.5
        weekly = 1 + 0.2 * (day.weekday() >= 5)
        base_rev = 50000 * trend * weekly * random.gauss(1, 0.08)
        base_ord = int(base_rev / random.uniform(180, 240))
        base_tra = int(base_ord * random.uniform(8, 12))
        rows.append((day.isoformat(), round(base_rev, 2), base_ord, base_tra))
    # 注入异常
    anomaly_idx = [120, 201, 330, 412, 478]
    for i in anomaly_idx:
        r = random.random()
        if r < 0.5:
            rows[i] = (rows[i][0], round(rows[i][1] * 1.8, 2), rows[i][2], rows[i][3])
        else:
            rows[i] = (rows[i][0], round(rows[i][1] * 0.4, 2), rows[i][2], rows[i][3])
    cur.executemany("INSERT INTO kpi VALUES (?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"已生成 {len(rows)} 条 KPI 数据（含 {len(anomaly_idx)} 处异常）-> {DB}")


if __name__ == "__main__":
    generate()
