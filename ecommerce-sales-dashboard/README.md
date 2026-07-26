# 电商销售分析看板（Streamlit + SQLite + SQL + Pandas）

> 面向数据分析岗位简历的实战项目：用 SQLite 模拟电商数据库，编写多表 JOIN 查询，使用 Pandas 清洗聚合，并通过 Streamlit 搭建交互式销售分析看板。

## 技术栈
- **数据库**：SQLite（关系型，模拟真实业务库）
- **SQL**：多表 JOIN、聚合、GROUP BY、窗口函数
- **分析**：Pandas 数据清洗与聚合
- **可视化**：Streamlit 交互式看板

## 项目结构
```
ecommerce-sales-dashboard/
├── generate_data.py      # 生成模拟电商数据库 ecommerce.db
├── app.py                # Streamlit 交互式看板
├── analysis_queries.sql  # 常用业务 SQL 查询示例
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py        # 生成 ecommerce.db
streamlit run app.py           # 启动看板（默认 http://localhost:8501）
```

## 看板内容
- 核心 KPI：总营收、订单数、活跃客户、最畅销产品
- 月度营收趋势（折线图）
- 品类销售、国家/地区销售（柱状图）
- Top 10 产品排行

## 简历表述参考
> 基于 SQLite 搭建模拟电商数据库，编写多表 JOIN 查询提取营收、趋势、客户分布等指标；使用 Pandas 完成数据清洗与聚合，通过 Streamlit 搭建交互式销售分析看板，可视化 GMV、品类结构、区域分布与 Top 商品，支撑业务快速洞察。
