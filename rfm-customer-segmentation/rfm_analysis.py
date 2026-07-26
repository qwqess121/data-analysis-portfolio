"""RFM 客户分层分析：评分 + 分群 + 可视化 + 导出 Power BI 数据集。"""
import sqlite3
import os
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "transactions.db")
OUT = os.path.join(BASE, "outputs")
FIG = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

SEG_MAP = {
    r"[1-2][1-2]": "流失客户(Hibernating)",
    r"[1-2][3-4]": "流失风险(At Risk)",
    r"[1-2]5": "可挽回(Can't Lose)",
    r"3[1-2]": "需关注(About to Sleep)",
    r"33": "潜力(Loyal)",
    r"[3-4][4-5]": "忠诚(Loyal)",
    r"41": "新客(New)",
    r"51": "新客(New)",
    r"[4-5][2-3]": "潜力忠诚(Potential)",
    r"5[4-5]": "冠军(Champions)",
}


def segment(r, f, m):
    if r >= 4 and f >= 4 and m >= 4:
        return "冠军(Champions)"
    if r >= 3 and f >= 3 and m >= 3:
        return "忠诚(Loyal)"
    if r <= 2 and f <= 2:
        return "流失客户(Hibernating)"
    if r <= 2 and f >= 3:
        return "流失风险(At Risk)"
    if r >= 4:
        return "新客/高活跃(New)"
    return "潜力客户(Potential)"


def run():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()

    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["amount"] = df["quantity"] * df["unit_price"]
    snapshot = df["invoice_date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        Recency=("invoice_date", lambda x: (snapshot - x.max()).days),
        Frequency=("invoice_no", "nunique"),
        Monetary=("amount", "sum"),
    ).reset_index()

    # 1-5 评分
    rfm["R_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_cell"] = rfm["R_score"].astype(str) + rfm["F_score"].astype(str)
    rfm["Segment"] = rfm.apply(lambda r: segment(r.R_score, r.F_score, r.M_score), axis=1)

    seg_summary = (
        rfm.groupby("Segment")
        .agg(客户数=("customer_id", "count"), 总营收=("Monetary", "sum"))
        .sort_values("总营收", ascending=False)
    )
    seg_summary["营收占比%"] = (seg_summary["总营收"] / seg_summary["总营收"].sum() * 100).round(1)
    seg_summary.to_csv(os.path.join(OUT, "segment_summary.csv"))
    rfm.to_csv(os.path.join(OUT, "rfm_customers.csv"), index=False)

    # 可视化
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    seg_summary["客户数"].plot(kind="bar", ax=ax[0], color="#4C72B0")
    ax[0].set_title("各客群客户数")
    ax[0].tick_params(axis="x", rotation=30)
    seg_summary["营收占比%"].plot(kind="bar", ax=ax[1], color="#DD8452")
    ax[1].set_title("各客群营收占比%")
    ax[1].tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "segment_distribution.png"), dpi=120)
    plt.close()

    champ_share = seg_summary.loc["冠军(Champions)", "营收占比%"] if "冠军(Champions)" in seg_summary.index else 0
    print("=== RFM 客户分层洞察 ===")
    print(seg_summary)
    print(f"\n冠军客群营收占比: {champ_share}%")
    print(f"输出: outputs/rfm_customers.csv, outputs/segment_summary.csv, figures/")


if __name__ == "__main__":
    run()
