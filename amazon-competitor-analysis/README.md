# 亚马逊竞品分析（Python + 市场洞察）

> 面向跨境电商数据分析岗位的实战项目：基于竞品 Listing 的 BSR 排名、价格、评论数、评分等维度，分析竞争格局、价格波动与评论增长，输出市场机会与风险洞察。

## 技术栈
- **数据处理**：Python + Pandas（竞品数据整合）
- **指标**：BSR 排名、价格变动率、评论增长率、评分、估计市场份额
- **可视化**：BSR 趋势、价格趋势对比图

## 项目结构
```
amazon-competitor-analysis/
├── generate_data.py        # 生成模拟竞品数据 competitor.db
├── competitor_analysis.py  # 竞品分析 + 可视化 + 报告
├── outputs/                # competitor_summary.csv
├── figures/                # competitor_trends.png
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py
python competitor_analysis.py
```

> 说明：本项目用模拟数据演示分析逻辑（真实场景可接入 Sorftime / 卖家精灵 等 MCP 数据源，理解 ACOS、TACOS、BSR、CVR 等跨境电商指标）。

## 核心输出
- 各竞品最新 BSR、价格变动、评论增长、评分、估计份额
- BSR 排名与价格趋势对比图
- 市场竞争格局与机会识别

## 简历表述参考
> 基于亚马逊竞品 Listing 数据，使用 Python 构建竞品分析流程，覆盖 BSR 排名、价格变动、评论增长、评分等维度，识别市场领先者与价格战信号，输出竞争格局报告与选品/定价建议，体现对跨境电商核心指标（BSR、ACOS、CVR 等）的理解。
