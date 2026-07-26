"""亚马逊竞品分析：BSR 排名、价格变动、评论增长、评分与竞争格局。"""
import sqlite3
import os
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "competitor.db")
OUT = os.path.join(BASE, "outputs")
FIG = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)


def run():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM listings", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])

    rows = []
    for asin, g in df.groupby("asin"):
        g = g.sort_values("date")
        first, last = g.iloc[0], g.iloc[-1]
        price_chg = (last["price"] - first["price"]) / first["price"] * 100
        review_growth = (last["reviews"] - first["reviews"]) / first["reviews"] * 100
        # 以 1/BSR 近似市场份额
        share = (1 / last["bsr"]) / sum(1 / df[df["date"] == last["date"]].groupby("asin")["bsr"].last())
        rows.append({
            "asin": asin, "name": last["name"],
            "最新BSR": int(last["bsr"]), "最新价格": last["price"],
            "价格变动%": round(price_chg, 1),
            "评论数": int(last["reviews"]), "评论增长%": round(review_growth, 1),
            "平均评分": round(g["rating"].mean(), 2),
            "估计份额%": round(share * 100, 1),
        })
    res = pd.DataFrame(rows).sort_values("最新BSR")
    res.to_csv(os.path.join(OUT, "competitor_summary.csv"), index=False)

    # 可视化：BSR 趋势 + 价格趋势
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    for asin, g in df.groupby("asin"):
        ax[0].plot(g["date"], g["bsr"], label=g.iloc[-1]["name"])
        ax[1].plot(g["date"], g["price"], label=g.iloc[-1]["name"])
    ax[0].invert_yaxis(); ax[0].set_title("BSR 排名趋势（越下越好）"); ax[0].legend(fontsize=8)
    ax[1].set_title("价格趋势"); ax[1].legend(fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "competitor_trends.png"), dpi=110); plt.close()

    top = res.iloc[0]
    print("=== 亚马逊竞品分析 ===")
    print(res.to_string(index=False))
    print(f"\n市场领先者: {top['name']} (BSR={top['最新BSR']}, 份额≈{top['估计份额%']}%)")
    print(f"输出: outputs/competitor_summary.csv, figures/competitor_trends.png")


if __name__ == "__main__":
    run()
