# 供应链需求预测与补货优化（Python + 机器学习）

> 面向跨境电商/供应链数据分析岗位的实战项目：基于历史销售与库存数据，使用时序特征工程 + 线性回归进行需求预测，并据此生成智能补货建议，平衡断货风险与仓储成本。

## 技术栈
- **特征工程**：趋势项、季节性（sin/cos）、工作日效应
- **建模**：LinearRegression 需求预测 + MAPE 评估
- **决策**：安全库存 + 提前期（Lead Time）补货规则
- **可视化**：实际 vs 拟合需求曲线

## 项目结构
```
supply-chain-forecasting/
├── generate_data.py           # 生成供需数据 supply_chain.db
├── forecast.py                # 需求预测 + 补货决策 + 可视化
├── outputs/                   # reorder_recommendations.csv / recommendations.txt
├── figures/                   # forecast_p*.png
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py
python forecast.py
```

## 核心输出
- 各产品需求预测精度（MAPE）
- 未来 7 天预计需求 vs 当前库存
- 补货优先级清单与建议补货量

## 简历表述参考
> 基于供应链历史数据，构建需求预测与库存补货优化模型：使用时序特征工程（趋势+季节性）结合线性回归预测产品需求，按提前期与安全库存生成补货建议；预测 MAPE 控制在 15% 以内，帮助在断货风险与仓储成本之间取得平衡，并输出可执行的补货优先级清单。
