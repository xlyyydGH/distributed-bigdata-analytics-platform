# 本地运行验证记录

验证时间：2026-05-15

## 已安装环境

- Java：`21.0.10 LTS`
- Python 虚拟环境：`.venv`
- 已安装核心依赖：
  - `pyspark 4.1.1`
  - `fastapi 0.136.1`
  - `uvicorn 0.47.0`
  - `pandas 3.0.3`
  - `mysql-connector-python 9.7.0`

## 已验证链路

### 1. 本地 Pandas 兜底链路

命令：

```powershell
.\scripts\run_small_demo.ps1
```

结果：

- 生成原始数据：`data/raw/users.csv`、`items.csv`、`events.csv`
- 生成指标表：`warehouse/marts/*.csv`
- 写入 SQLite：`warehouse/analytics.db`
- 生成报表：`warehouse/reports/dashboard.html`

### 2. PySpark 离线计算链路

命令：

```powershell
.\scripts\run_spark_local.ps1
```

结果：

- Spark 能正常启动并执行 DataFrame 计算
- 输出指标表：
  - `warehouse/spark_marts/daily_overview.csv`
  - `warehouse/spark_marts/category_sales.csv`
  - `warehouse/spark_marts/top_items.csv`

说明：

Windows 本地 PySpark 可能打印 `winutils.exe` 相关 warning，这是 Hadoop 本地文件系统的 Windows 兼容提示。本项目本地演示模式默认让 Spark 完成计算、Python 写出小规模指标 CSV，因此不影响验证结果。Linux/Kubernetes 集群环境可使用 `--native-output` 走 Spark 原生写出。

### 3. FastAPI 指标查询链路

命令：

```powershell
.\scripts\start_api.ps1
```

接口：

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/metrics/daily?limit=2`
- `http://127.0.0.1:8000/metrics/categories?limit=3`
- `http://127.0.0.1:8000/metrics/top-items?limit=5`
- `http://127.0.0.1:8000/metrics/retention?limit=10`

已验证 `/health`、`/metrics/daily`、`/metrics/categories` 可正常返回 JSON。

