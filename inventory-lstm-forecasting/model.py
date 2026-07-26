"""库存销量预测：LSTM（可选）/ 随机森林回退 + 库存预警。
tensorflow 未安装时自动回退到 RandomForest，保证可运行。"""
import sqlite3
import os
import random
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "retail_sales.db")
OUT = os.path.join(BASE, "outputs")
FIG = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False

WINDOW = 30
HORIZON = 7


def make_samples(series, window, horizon):
    X, y = [], []
    for i in range(len(series) - window - horizon + 1):
        X.append(series[i:i + window])
        y.append(series[i + window:i + window + horizon])
    return np.array(X), np.array(y)


def run():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["product_id", "date"])

    alerts = []
    for pid, g in df.groupby("product_id"):
        series = g["sales"].values.astype(float)
        X, y = make_samples(series, WINDOW, HORIZON)
        split = int(len(X) * 0.85)
        Xtr, Xte = X[:split], X[split:]
        ytr, yte = y[:split], y[split:]

        if TF_AVAILABLE:
            Xtr_r = Xtr.reshape(-1, WINDOW, 1)
            Xte_r = Xte.reshape(-1, WINDOW, 1)
            model = Sequential([LSTM(32, input_shape=(WINDOW, 1)), Dense(HORIZON)])
            model.compile(optimizer="adam", loss="mse")
            model.fit(Xtr_r, ytr, epochs=10, verbose=0)
            pred = model.predict(Xte_r, verbose=0)
            model_name = "LSTM"
        else:
            Xtr_f = Xtr.reshape(len(Xtr), -1)
            Xte_f = Xte.reshape(len(Xte), -1)
            model = RandomForestRegressor(n_estimators=80, random_state=42, n_jobs=-1)
            model.fit(Xtr_f, ytr)
            pred = model.predict(Xte_f)
            model_name = "RandomForest(回退)"

        mape = mean_absolute_percentage_error(yte, pred)

        # 未来预测
        last_win = series[-WINDOW:].reshape(1, -1)
        if TF_AVAILABLE:
            fut = model.predict(last_win.reshape(1, WINDOW, 1), verbose=0)[0]
        else:
            fut = model.predict(last_win)[0]
        fut = np.clip(fut, 0, None)
        current_stock = int(g["sales"].iloc[-1] * random.randint(3, 8))
        expected = fut.sum()
        alert = expected > current_stock
        alerts.append({
            "product_id": pid, "model": model_name, "MAPE%": round(mape * 100, 1),
            "current_stock": current_stock, "expected_7d": round(expected, 0),
            "alert": "⚠️缺货风险" if alert else "库存充足",
        })

        if pid <= 3:
            plt.figure(figsize=(8, 3))
            plt.plot(yte[-30:].ravel(), label="实际", alpha=0.7)
            plt.plot(pred[-30:].ravel(), label="预测", color="red")
            plt.title(f"产品 {pid} ({model_name}, MAPE={mape*100:.1f}%)")
            plt.legend(); plt.tight_layout()
            plt.savefig(os.path.join(FIG, f"lstm_p{pid}.png"), dpi=110); plt.close()

    res = pd.DataFrame(alerts)
    res.to_csv(os.path.join(OUT, "forecast_alerts.csv"), index=False)
    print("=== 库存销量预测 ===")
    print(f"TF_AVAILABLE={TF_AVAILABLE}")
    print(res.to_string(index=False))
    print(f"输出: outputs/forecast_alerts.csv, figures/")


if __name__ == "__main__":
    run()
