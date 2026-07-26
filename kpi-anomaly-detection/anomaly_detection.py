"""KPI 异常检测：滚动 Z-Score + IQR 统计法，输出异常标记与可视化。"""
import sqlite3
import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "kpi.db")
OUT = os.path.join(BASE, "outputs")
FIG = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)


def detect(series, window=30, k=3.0):
    roll_mean = series.rolling(window, min_periods=10).mean()
    roll_std = series.rolling(window, min_periods=10).std().fillna(series.std())
    z = (series - roll_mean) / roll_std
    return (z.abs() > k).astype(int), z


def run():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM kpi", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    flag, z = detect(df["revenue"])
    df["anomaly"] = flag
    df["z_score"] = z.round(2)

    out = df[["date", "revenue", "orders", "traffic", "z_score", "anomaly"]]
    out.to_csv(os.path.join(OUT, "kpi_anomaly_output.csv"), index=False)

    plt.figure(figsize=(10, 4))
    plt.plot(df["date"], df["revenue"], label="营收", alpha=0.7)
    an = df[df["anomaly"] == 1]
    plt.scatter(an["date"], an["revenue"], color="red", label=f"异常({len(an)})", zorder=5)
    plt.title("KPI 异常检测（营收）")
    plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(FIG, "kpi_anomaly.png"), dpi=110); plt.close()

    print("=== KPI 异常检测 ===")
    print(f"检测到的异常天数: {int(df['anomaly'].sum())} / {len(df)}")
    print(an[["date", "revenue", "z_score"]].to_string(index=False))
    print(f"输出: outputs/kpi_anomaly_output.csv, figures/kpi_anomaly.png")


if __name__ == "__main__":
    run()
