# K-Means 客户聚类分析（Python + 无监督学习）

> 面向数据分析岗位的进阶项目：基于电商交易数据，使用 RFM 特征工程结合 K-Means 无监督学习进行客户细分，通过肘部法与轮廓系数确定最优聚类数，并利用 PCA 降维可视化客户群体。

## 技术栈
- **特征工程**：RFM（最近购买、频次、金额）+ 标准化（StandardScaler）
- **建模**：K-Means 聚类（scikit-learn）
- **评估**：肘部法（Elbow）、轮廓系数（Silhouette）
- **可视化**：PCA 2D 降维散点图、评估曲线

## 项目结构
```
kmeans-customer-clustering/
├── generate_data.py     # 生成模拟交易数据 transactions.db
├── clustering.py        # RFM + K-Means + 评估 + PCA 可视化
├── outputs/             # cluster_profile.csv / rfm_with_clusters.csv
├── figures/             # elbow_silhouette.png / cluster_pca.png
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py
python clustering.py
```

## 核心输出
- 最优聚类数（肘部法 + 轮廓系数）
- 各聚类 RFM 均值画像
- PCA 2D 客户群体可视化

## 简历表述参考
> 基于电商交易数据，使用 RFM 特征工程结合 K-Means 无监督学习进行客户细分；通过肘部法与轮廓系数确定最优聚类数（k=4），利用 PCA 降维可视化客户群体，输出不同价值客群的经营策略，相比规则式 RFM 提升了分群的客观性与可解释性。
