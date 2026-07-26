"""K-Means 客户聚类：RFM 特征工程 + 肘部法/轮廓系数 + PCA 可视化。"""
import sqlite3
import os
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "transactions.db")
OUT = os.path.join(BASE, "outputs")
FIG = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)


def run():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["amount"] = df["quantity"] * df["unit_price"]
    snap = df["invoice_date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        Recency=("invoice_date", lambda x: (snap - x.max()).days),
        Frequency=("invoice_no", "nunique"),
        Monetary=("amount", "sum"),
    )
    X = StandardScaler().fit_transform(rfm[["Recency", "Frequency", "Monetary"]])

    # 肘部法 + 轮廓系数
    ks = range(2, 11)
    inertia, sil = [], []
    for k in ks:
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
        inertia.append(km.inertia_)
        sil.append(silhouette_score(X, km.labels_))

    best_k = int(ks[np.argmax(sil)])
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10).fit(X)
    rfm["Cluster"] = km.labels_

    # PCA 2D 可视化
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X)
    rfm["PC1"], rfm["PC2"] = coords[:, 0], coords[:, 1]

    # 聚类画像
    profile = rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]].mean().round(1)
    profile.to_csv(os.path.join(OUT, "cluster_profile.csv"))
    rfm.to_csv(os.path.join(OUT, "rfm_with_clusters.csv"))

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(list(ks), inertia, "o-")
    ax[0].set_title("肘部法 (Elbow)")
    ax[0].set_xlabel("k"); ax[0].set_ylabel("Inertia")
    ax[1].plot(list(ks), sil, "o-", color="green")
    ax[1].set_title("轮廓系数 (Silhouette)")
    ax[1].set_xlabel("k"); ax[1].set_ylabel("Score")
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "elbow_silhouette.png"), dpi=120); plt.close()

    plt.figure(figsize=(6, 5))
    plt.scatter(rfm["PC1"], rfm["PC2"], c=rfm["Cluster"], cmap="tab10", s=12)
    plt.title(f"客户聚类 (PCA 2D, k={best_k})")
    plt.xlabel("PC1"); plt.ylabel("PC2")
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "cluster_pca.png"), dpi=120); plt.close()

    print("=== K-Means 客户聚类 ===")
    print(f"最优聚类数 k = {best_k} (轮廓系数最高)")
    print(profile)
    print(f"输出: outputs/cluster_profile.csv, outputs/rfm_with_clusters.csv, figures/")


if __name__ == "__main__":
    run()
