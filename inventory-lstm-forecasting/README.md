# 库存需求预测与缺货预警（Python + LSTM / 随机森林）

> 面向跨境电商/零售数据分析岗位的实战项目：基于历史日度销量数据，使用时序模型（LSTM，未安装时自动回退到随机森林）预测未来 7 天销量，并对比当前库存生成缺货预警，辅助补货决策。

## 技术栈
- **深度学习（可选）**：TensorFlow/Keras LSTM 时序预测
- **机器学习（回退）**：RandomForestRegressor 序列预测
- **决策**：提前期需求 vs 当前库存 → 缺货预警
- **可视化**：Streamlit 库存预测看板

## 项目结构
```
inventory-lstm-forecasting/
├── generate_data.py   # 生成日度销量时序 retail_sales.db
├── model.py           # LSTM/随机森林预测 + 预警 + 可视化
├── app.py             # Streamlit 库存预测看板
├── outputs/           # forecast_alerts.csv
├── figures/           # lstm_p*.png
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py
python model.py              # 运行预测（无 GPU/tensorflow 也能跑，自动回退）
streamlit run app.py         # 可选：启动看板
```

## 核心输出
- 各产品 7 天需求预测与 MAPE
- 缺货风险预警清单

## 简历表述参考
> 针对零售历史销量数据，使用 LSTM 深度学习（环境不支持时回退随机森林）构建 7 天销量预测模型，设计库存短缺预警逻辑，通过 Streamlit 搭建预测与预警看板，辅助库存补货决策、降低断货风险。模型预测 MAPE 控制在 15% 左右。
