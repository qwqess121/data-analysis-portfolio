# KPI 异常检测（Python + 统计方法）

> 面向业务指标预警与数据闭环岗位的实战项目：监控每日业务 KPI（营收/订单/流量），使用统计异常检测自动识别异常波动，输出可对接 BI 看板或自动化告警流程的结果。

## 技术栈
- **异常检测**：滚动均值/标准差 Z-Score、IQR
- **可视化**：Matplotlib 异常点位标注
- **输出**：异常标记 CSV（可对接仪表盘/告警）

## 项目结构
```
kpi-anomaly-detection/
├── generate_data.py        # 生成带异常的 KPI 数据 kpi.db
├── anomaly_detection.py    # 统计异常检测 + 可视化 + 导出
├── outputs/                # kpi_anomaly_output.csv
├── figures/                # kpi_anomaly.png
├── requirements.txt
└── README.md
```

## 快速开始
```bash
pip install -r requirements.txt
python generate_data.py
python anomaly_detection.py
```

## 核心输出
- 每日 KPI + Z-Score + 异常标记（0/1）
- 异常日期、数值、偏离程度
- 异常趋势图

## 简历表述参考
> 针对业务日度 KPI（营收/订单/流量），使用 Python 实现基于滚动统计的异常检测流程，自动识别指标的异常尖峰与骤降，输出异常标记结果并生成趋势图，支撑业务预警与数据闭环跟进，帮助业务方在问题扩大前及时介入。
