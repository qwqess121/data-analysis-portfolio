# 电商 SQL + BI 分析流水线（Python + SQL + Power BI）

> 面向数据分析岗位的端到端实战项目：基于模拟巴西电商（Olist 风格）真实业务场景（数万级订单），完成「数据生成 → SQL 清洗分析 → 导出 Power BI 数据集 → 商业洞察」全流程。

## 技术栈
- **数据库**：SQLite（关系型，多表关联）
- **SQL**：JOIN、聚合、窗口函数、CASE WHEN、日期函数
- **分析**：Python + Pandas（ETL、指标计算）
- **BI**：导出 CSV/Excel，可直接在 Power BI / Tableau / FineBI 中建模

## 项目结构
```
ecommerce-sql-bi-pipeline/
├── generate_data.py   # 生成模拟电商数据库 (订单/明细/客户/产品)
├── etl_clean.py       # SQL 业务分析 + 导出 Power BI 数据集
├── queries.sql        # 常用业务 SQL 查询示例
├── outputs/           # 导出的分析结果与明细宽表
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py    # 生成 ecommerce.db
python etl_clean.py        # 运行分析并导出 outputs/*.csv
```
将 `outputs/order_detail.csv` 导入 Power BI，即可搭建营收、品类、区域、物流时效、复购等看板。

## 核心分析模块
- 月度营收趋势 & 峰值识别
- 品类销售结构
- 各州销售与物流时效对比
- 客户复购率（留存分析）
- 订单取消率监控

## 简历表述参考
> 基于模拟电商真实业务数据（数万级订单），使用 Python 完成数据清洗与特征工程，构建 SQLite 关系型数据库并编写 20+ 条业务 SQL，分析 GMV、品类结构、区域分布、客户复购与物流时效等核心指标；导出标准化数据集供 Power BI 建模，识别 90%+ 客户为一次性购买等留存问题，输出可落地的运营优化建议。
