# 数据分析简历项目集（8 个开源实战项目）

> 本目录包含 8 个可直接写进简历的数据分析实战项目，覆盖你提供的 5 类 JD 核心能力：电商运营分析、BI 看板、客户分层、库存预测、竞品分析、KPI 异常检测。
> 每个项目**独立文件夹 + 自带数据生成器**，无需外部数据/API 即可一键运行，产出数据库、CSV 报表与可视化图表。

## 运行环境
```bash
pip install pandas numpy matplotlib seaborn scikit-learn sqlalchemy streamlit openpyxl
# 库存 LSTM 项目可选：pip install tensorflow（未安装会自动回退随机森林）
```
> 验证时使用了本机 Anaconda Python 3.12.7（已自带上述核心库）。各项目脚本使用相对路径，在各自文件夹内运行即可。

## 项目总览（对应岗位能力）

| # | 项目 | 技术栈 | 对应 JD 能力 | 核心产出 |
|---|------|--------|--------------|----------|
| 1 | [ecommerce-sales-dashboard](./ecommerce-sales-dashboard) | SQLite + SQL + Pandas + Streamlit | BI 看板 / SQL | 交互式销售看板 |
| 2 | [ecommerce-sql-bi-pipeline](./ecommerce-sql-bi-pipeline) | Python + SQL + Power BI 数据集 | SQL+BI 全链路 | 订单/品类/区域/复购分析 + Power BI 数据集 |
| 3 | [rfm-customer-segmentation](./rfm-customer-segmentation) | Python + RFM + 可视化 | 客户/品牌消费者分析 | 客户分层 + 营收贡献 |
| 4 | [kmeans-customer-clustering](./kmeans-customer-clustering) | Python + K-Means + PCA | 进阶客户细分 | 聚类画像 + 降维可视化 |
| 5 | [supply-chain-forecasting](./supply-chain-forecasting) | Python + 线性回归 + 补货规则 | 库存/供应链预测 | 需求预测 + 补货建议 |
| 6 | [inventory-lstm-forecasting](./inventory-lstm-forecasting) | Python + LSTM/随机森林 + Streamlit | 库存预测 + AI | 7天预测 + 缺货预警 |
| 7 | [kpi-anomaly-detection](./kpi-anomaly-detection) | Python + 统计异常检测 | 指标预警/数据闭环 | 异常标记 + 趋势图 |
| 8 | [amazon-competitor-analysis](./amazon-competitor-analysis) | Python + 竞品指标 | 竞品/市场洞察 | 竞争格局报告 |

## 快速开始（以项目 2 为例）
```bash
cd ecommerce-sql-bi-pipeline
python generate_data.py     # 生成模拟数据
python etl_clean.py         # 运行分析并导出 outputs/
```
将 `outputs/order_detail.csv` 导入 Power BI / Tableau / FineBI 即可搭建看板。

## 推荐组合（按求职方向）
- **通用数据分析 / 策略运营**：项目 1 + 2 + 3
- **跨境电商数据分析**：项目 5 + 6 + 8 + 7
- **品牌 / 消费者分析**：项目 3 + 4 + 2

## 说明
- 所有数据均为**程序生成的模拟数据**，可放心公开、复现、改写。

## 🌐 在线部署（Streamlit Community Cloud，免费）
本项目已配置好根目录 `requirements.txt` 与入口 `dashboard.py`，可一键部署到 https://share.streamlit.io：

1. 打开 https://share.streamlit.io ，用 **GitHub 账号登录**（OAuth 授权一次即可）。
2. 点击 **New app** → 选择本仓库 `qwqess121/data-analysis-portfolio`。
3. 设置：
   - **Main file path**：`dashboard.py`
   - **Branch**：`main`
4. 点击 **Deploy**，等待 1–2 分钟，即可获得公开访问链接。

> 之后每次 `git push` 到 `main` 分支，Streamlit Cloud 会自动重新部署。
- 图表使用本机中文字体（Microsoft YaHei / SimHei）渲染；若在其他环境乱码，安装中文字体或将图中文字改为英文即可。
- 想更贴近目标行业，可把模拟数据替换为真实业务数据（如公司脱敏数据、Kaggle 公开数据集），改写 README 中的业务背景即可。

## 统一 BI 看板（一键启动所有项目）

`dashboard.py` 把 8 个项目整合进一个 **BI 风格交互看板**（侧边栏导航 + KPI 卡片 + Plotly 交互图表：悬停/缩放/框选/下钻），每个项目都支持**上传你自己的 CSV** 复用分析，或一键运行内置示例。

```bash
# 需要依赖：pip install pandas numpy plotly streamlit sqlalchemy openpyxl
python dashboard.py
# 浏览器打开 http://localhost:8501
```

### 🛢️ 数据连接工作台（Power BI 风格 · 参考开源项目）

看板内置一个独立的 **「数据连接工作台」** 页面，能力对标 Power BI / Tableau 的「获取数据 + 分析」流程：

- **多种数据源接入**（像 Power BI 的 Get Data）
  - CSV / Excel 上传（Excel 自动识别多 Sheet）
  - SQLite 数据库文件上传
  - **数据库连接（SQLAlchemy URI）**：PostgreSQL / MySQL / SQL Server / SQLite，粘贴连接串即可连真实库
  - 一键加载内置电商示例库即时体验
- **SQL 查询（SQL Lab）**：编写并运行 SQL，结果即时表格化（借鉴 Apache Superset）
- **自动数据画像**：列类型 / 缺失率 / 唯一值（借鉴 ydata-profiling）
- **交互式可视化（字段面板）**：选择 X 轴 / Y 轴 / 聚合方式 / 颜色分组 / 图表类型（柱状、折线、面积、散点、饼、箱线、直方图、相关性热力图），即所见即所得地拖字段出图（借鉴 PyGWalker 的拖拽探索、Metabase 的 GUI 问数、Evidence 的 SQL 驱动）
- 上传的 CSV/Excel 会自动落进一个临时 SQLite，因此**同一套 SQL Lab + 图表构建器**对文件和数据库通用

> 开源参考：PyGWalker（拖拽探索）、Apache Superset（SQL Lab）、Evidence（SQL 驱动应用）、Metabase（GUI 即席查询）、ydata-profiling（一键 EDA）。
> 若需更强的「拖拽式」体验，可 `pip install pygwalker` 后在工作台中扩展（本项目为保证可稳定运行，默认采用自研字段面板，零额外重依赖）。
