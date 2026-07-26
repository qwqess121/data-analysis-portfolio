"""供应链需求预测与补货优化：时序特征工程 + 线性回归预测 + 补货决策。"""
import sqlite3
import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "supply_chain.db")
OUT = os.path.join(BASE, "outputs")
FIG = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

LEAD_TIME = 7
SAFETY = 1.2


def run():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM demand", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["product_id", "date"])

    recs = []
    for pid, g in df.groupby("product_id"):
        g = g.reset_index(drop=True)
        g["t"] = np.arange(len(g))
        g["doy"] = g["date"].dt.dayofyear
        g["sin"] = np.sin(2 * np.pi * g["doy"] / 365)
        g["cos"] = np.cos(2 * np.pi * g["doy"] / 365)
        train = g.iloc[:-LEAD_TIME]
        test = g.iloc[-LEAD_TIME:]
        X = train[["t", "sin", "cos"]].values
        y = train["demand"].values
        model = LinearRegression().fit(X, y)
        Xte = test[["t", "sin", "cos"]].values
        pred = model.predict(Xte)
        mape = mean_absolute_percentage_error(test["demand"], pred)

        # 未来 7 天预测 + 补货决策
        last = g.iloc[-1]
        future_t = np.arange(len(g), len(g) + LEAD_TIME)
        future_doy = [(last["date"] + pd.Timedelta(days=i + 1)).dayofyear for i in range(LEAD_TIME)]
        Xf = np.column_stack([
            future_t,
            np.sin(2 * np.pi * np.array(future_doy) / 365),
            np.cos(2 * np.pi * np.array(future_doy) / 365),
        ])
        fut_pred = model.predict(Xf)
        expected_demand = fut_pred.sum() * SAFETY
        current_inv = int(last["inventory"])
        reorder = expected_demand > current_inv
        recs.append({
            "product_id": pid, "MAPE%": round(mape * 100, 1),
            "current_inventory": current_inv,
            "expected_7d_demand": round(expected_demand, 0),
            "reorder": "是" if reorder else "否",
            "reorder_qty": max(0, int(round(expected_demand - current_inv))),
        })

        # 可视化（仅前 4 个产品）
        if pid <= 4:
            plt.figure(figsize=(8, 3))
            plt.plot(g["date"], g["demand"], label="实际", alpha=0.6)
            plt.plot(g["date"].iloc[:-LEAD_TIME], model.predict(X), label="拟合", color="red")
            plt.title(f"产品 {pid} 需求预测 (MAPE={mape*100:.1f}%)")
            plt.legend(); plt.tight_layout()
            plt.savefig(os.path.join(FIG, f"forecast_p{pid}.png"), dpi=110); plt.close()

    rec_df = pd.DataFrame(recs)
    rec_df.to_csv(os.path.join(OUT, "reorder_recommendations.csv"), index=False)
    with open(os.path.join(OUT, "recommendations.txt"), "w", encoding="utf-8") as f:
        f.write("供应链补货建议\n" + "=" * 30 + "\n")
        for _, r in rec_df.iterrows():
            if r["reorder"] == "是":
                f.write(f"产品 {r['product_id']}: 当前库存 {r['current_inventory']}，"
                        f"未来7天预计需求 {int(r['expected_7d_demand'])}，建议补货 {int(r['reorder_qty'])} 件\n")

    need = (rec_df["reorder"] == "是").sum()
    print("=== 供应链需求预测与补货 ===")
    print(rec_df.to_string(index=False))
    print(f"\n需补货产品数: {need}/{len(rec_df)}")
    print(f"输出: outputs/reorder_recommendations.csv, outputs/recommendations.txt, figures/")


if __name__ == "__main__":
    run()
