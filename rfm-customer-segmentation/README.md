# RFM 客户分层分析（Python + 客户价值模型）

> 面向品牌/消费者数据分析岗位的实战项目：基于电商交易数据，使用 RFM（最近购买、购买频次、消费金额）模型对客户进行价值分层，识别高价值客群并给出差异化运营策略。

## 技术栈
- **数据处理**：Python + Pandas（数据清洗、特征工程）
- **建模**：RFM 评分（分位数分箱 1-5）+ 规则分群
- **可视化**：Matplotlib（客群分布、营收贡献）
- **BI 衔接**：导出 CSV 供 Power BI 建模

## 项目结构
```
rfm-customer-segmentation/
├── generate_data.py    # 生成模拟电商交易数据 transactions.db
├── rfm_analysis.py     # RFM 评分 + 分群 + 可视化 + 导出
├── outputs/            # rfm_customers.csv / segment_summary.csv
├── figures/            # 客群分布图
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py
python rfm_analysis.py
```

## 核心输出
- 客户级 RFM 评分与客群标签（冠军/忠诚/潜力/流失风险/流失客户）
- 各客群客户数、总营收、营收占比
- 客群分布可视化图

## 简历表述参考
> 基于电商交易数据，使用 Python 构建 RFM 客户价值模型，将客户划分为 Champions、Loyal、At-Risk、Hibernating 等 8 类；发现 25% 高价值客户贡献 66% 营收，针对流失风险客群设计再营销触达策略，并输出 Power BI 客户分层仪表盘，支撑精准营销与会员运营。
