# Milvus 表召回测试报告

- 运行时间：2026-09-28T18:19:39+08:00
- 测试集：40 条
- 向量模型：`text-embedding-v3`
- Top-K：4
- 真实表：dim_customers, dim_products, sales_orders, exchange_rates, finance_expenses
- 干扰表：hr_attendance_records, iot_device_alerts, legal_contract_archive, warehouse_temperature_logs

## 汇总指标

| 指标 | 数值 |
|---|---:|
| Mean Recall@K | 92.5% |
| 全部必需表命中率 | 75.0% |
| MRR@K | 0.9250 |
| Top-K 干扰表总数 | 9 |

## 逐表召回率

| 表名 | 必需用例数 | Top-K 命中 | 漏召回 | 召回率 |
|---|---:|---:|---:|---:|
| `dim_customers` | 9 | 9 | 0 | 100.0% |
| `dim_products` | 24 | 23 | 1 | 95.8% |
| `sales_orders` | 31 | 31 | 0 | 100.0% |
| `exchange_rates` | 25 | 16 | 9 | 64.0% |
| `finance_expenses` | 6 | 6 | 0 | 100.0% |

## 逐条结果

### [1] 查询所有客户的客户编号、客户名称、客户类型、所属行业和国家。

- 状态：**通过**
- 必须召回：`dim_customers`
- Top-4 命中：`dim_customers`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.708380 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.635874 | 真实表-非必需 | 是 |
| 3 | `dim_products` | 0.532229 | 真实表-非必需 | 是 |
| 4 | `legal_contract_archive` | 0.524416 | 干扰表 | 是 |
| 5 | `finance_expenses` | 0.515258 | 真实表-非必需 | 否 |
| 6 | `hr_attendance_records` | 0.503243 | 干扰表 | 否 |
| 7 | `warehouse_temperature_logs` | 0.493272 | 干扰表 | 否 |
| 8 | `exchange_rates` | 0.474752 | 真实表-非必需 | 否 |
| 9 | `iot_device_alerts` | 0.438371 | 干扰表 | 否 |

### [2] 查询所有产品的产品名称、产品线、类别和技术路线。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-4 命中：`dim_products`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.640702 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.556611 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.528713 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.515264 | 真实表-非必需 | 是 |
| 5 | `iot_device_alerts` | 0.499310 | 干扰表 | 否 |
| 6 | `warehouse_temperature_logs` | 0.484651 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.449986 | 干扰表 | 否 |
| 8 | `legal_contract_archive` | 0.411797 | 干扰表 | 否 |
| 9 | `exchange_rates` | 0.379515 | 真实表-非必需 | 否 |

### [3] 查询所有已完成订单的订单号、客户编号、产品编号、订单日期和订单金额。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-4 命中：`sales_orders`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.743630 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.588933 | 真实表-非必需 | 是 |
| 3 | `dim_products` | 0.550742 | 真实表-非必需 | 是 |
| 4 | `hr_attendance_records` | 0.546815 | 干扰表 | 是 |
| 5 | `warehouse_temperature_logs` | 0.541176 | 干扰表 | 否 |
| 6 | `finance_expenses` | 0.527100 | 真实表-非必需 | 否 |
| 7 | `legal_contract_archive` | 0.504164 | 干扰表 | 否 |
| 8 | `exchange_rates` | 0.487406 | 真实表-非必需 | 否 |
| 9 | `iot_device_alerts` | 0.477537 | 干扰表 | 否 |

### [4] 查询每种产品的材料成本和人工成本。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-4 命中：`dim_products`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.648163 | 真实表-非必需 | 是 |
| 2 | `dim_products` | 0.600935 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.554343 | 真实表-非必需 | 是 |
| 4 | `hr_attendance_records` | 0.540532 | 干扰表 | 是 |
| 5 | `warehouse_temperature_logs` | 0.528269 | 干扰表 | 否 |
| 6 | `iot_device_alerts` | 0.503606 | 干扰表 | 否 |
| 7 | `dim_customers` | 0.479045 | 真实表-非必需 | 否 |
| 8 | `exchange_rates` | 0.459370 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.414269 | 干扰表 | 否 |

### [5] 查询每种产品的单位实际成本，实际成本定义为材料成本加人工成本。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-4 命中：`dim_products`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.645230 | 真实表-非必需 | 是 |
| 2 | `dim_products` | 0.571496 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.563987 | 真实表-非必需 | 是 |
| 4 | `hr_attendance_records` | 0.529081 | 干扰表 | 是 |
| 5 | `warehouse_temperature_logs` | 0.503422 | 干扰表 | 否 |
| 6 | `exchange_rates` | 0.484885 | 真实表-非必需 | 否 |
| 7 | `iot_device_alerts` | 0.464835 | 干扰表 | 否 |
| 8 | `dim_customers` | 0.463184 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.419733 | 干扰表 | 否 |

### [6] 查询每个国家有多少客户。

- 状态：**通过**
- 必须召回：`dim_customers`
- Top-4 命中：`dim_customers`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.624739 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.568614 | 真实表-非必需 | 是 |
| 3 | `exchange_rates` | 0.522715 | 真实表-非必需 | 是 |
| 4 | `warehouse_temperature_logs` | 0.466110 | 干扰表 | 是 |
| 5 | `dim_products` | 0.451102 | 真实表-非必需 | 否 |
| 6 | `hr_attendance_records` | 0.446378 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.435700 | 干扰表 | 否 |
| 8 | `finance_expenses` | 0.427987 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.396605 | 干扰表 | 否 |

### [7] 查询每个产品类别有多少种产品。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-4 命中：`dim_products`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.598069 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.546233 | 真实表-非必需 | 是 |
| 3 | `dim_customers` | 0.523541 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.485487 | 真实表-非必需 | 是 |
| 5 | `warehouse_temperature_logs` | 0.480905 | 干扰表 | 否 |
| 6 | `iot_device_alerts` | 0.472468 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.445938 | 干扰表 | 否 |
| 8 | `exchange_rates` | 0.420266 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.397798 | 干扰表 | 否 |

### [8] 查询已完成订单的总销售数量。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-4 命中：`sales_orders`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.701739 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.541613 | 真实表-非必需 | 是 |
| 3 | `dim_products` | 0.488880 | 真实表-非必需 | 是 |
| 4 | `hr_attendance_records` | 0.486366 | 干扰表 | 是 |
| 5 | `warehouse_temperature_logs` | 0.481178 | 干扰表 | 否 |
| 6 | `exchange_rates` | 0.470512 | 真实表-非必需 | 否 |
| 7 | `iot_device_alerts` | 0.446736 | 干扰表 | 否 |
| 8 | `finance_expenses` | 0.442945 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.414788 | 干扰表 | 否 |

### [9] 查询2025年的已完成订单数量。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-4 命中：`sales_orders`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.614682 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.529262 | 真实表-非必需 | 是 |
| 3 | `dim_products` | 0.476474 | 真实表-非必需 | 是 |
| 4 | `warehouse_temperature_logs` | 0.455631 | 干扰表 | 是 |
| 5 | `hr_attendance_records` | 0.450448 | 干扰表 | 否 |
| 6 | `iot_device_alerts` | 0.448827 | 干扰表 | 否 |
| 7 | `exchange_rates` | 0.444555 | 真实表-非必需 | 否 |
| 8 | `finance_expenses` | 0.437545 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.409481 | 干扰表 | 否 |

### [10] 查询2025年每个月的已完成订单数量。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-4 命中：`sales_orders`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.644066 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.546034 | 真实表-非必需 | 是 |
| 3 | `warehouse_temperature_logs` | 0.490290 | 干扰表 | 是 |
| 4 | `dim_products` | 0.488824 | 真实表-非必需 | 是 |
| 5 | `hr_attendance_records` | 0.470787 | 干扰表 | 否 |
| 6 | `finance_expenses` | 0.466053 | 真实表-非必需 | 否 |
| 7 | `exchange_rates` | 0.461146 | 真实表-非必需 | 否 |
| 8 | `iot_device_alerts` | 0.458154 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.418843 | 干扰表 | 否 |

### [11] 查询2025年的销售收入，收入按照不含税销售收入计算，并统一换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `exchange_rates`
- Top-4 命中：`sales_orders`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.609027 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.557915 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.504114 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.499978 | 真实表-非必需 | 是 |
| 5 | `dim_products` | 0.475265 | 真实表-非必需 | 否 |
| 6 | `hr_attendance_records` | 0.447680 | 干扰表 | 否 |
| 7 | `warehouse_temperature_logs` | 0.426913 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.393247 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.380900 | 干扰表 | 否 |

### [12] 查询2025年每个销售区域的收入，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `exchange_rates`
- Top-4 命中：`sales_orders`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.561805 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.539474 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.529652 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.485984 | 真实表-非必需 | 是 |
| 5 | `dim_products` | 0.485624 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.445888 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.415548 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.407293 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.331890 | 干扰表 | 否 |

### [13] 查询2025年每个产品的销售收入，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.588024 | 必须召回 | 是 |
| 2 | `dim_products` | 0.554460 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.540946 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.517940 | 真实表-非必需 | 是 |
| 5 | `finance_expenses` | 0.515714 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.463063 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.429294 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.426129 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.361131 | 干扰表 | 否 |

### [14] 查询2025年每个产品的销售成本，销售成本定义为材料成本加人工成本后乘以销售数量。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`
- Top-4 命中：`sales_orders`, `dim_products`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.631154 | 真实表-非必需 | 是 |
| 2 | `sales_orders` | 0.607335 | 必须召回 | 是 |
| 3 | `dim_products` | 0.568764 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.479991 | 真实表-非必需 | 是 |
| 5 | `hr_attendance_records` | 0.460086 | 干扰表 | 否 |
| 6 | `exchange_rates` | 0.452429 | 真实表-非必需 | 否 |
| 7 | `warehouse_temperature_logs` | 0.419539 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.388282 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.370601 | 干扰表 | 否 |

### [15] 查询2025年每个产品的收入和毛利，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.576988 | 真实表-非必需 | 是 |
| 2 | `dim_products` | 0.575580 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.540277 | 必须召回 | 是 |
| 4 | `exchange_rates` | 0.521476 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.504718 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.499364 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.443803 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.416200 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.362951 | 干扰表 | 否 |

### [16] 查询2025年每个产品的毛利率，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.594849 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.558796 | 真实表-非必需 | 是 |
| 3 | `exchange_rates` | 0.548296 | 必须召回 | 是 |
| 4 | `sales_orders` | 0.509766 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.501680 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.497376 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.417190 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.391774 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.371910 | 干扰表 | 否 |

### [17] 查询2025年每个客户的销售收入，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_customers`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.611688 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.583980 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.554903 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.499813 | 真实表-非必需 | 是 |
| 5 | `dim_products` | 0.497991 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.457114 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.436227 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.402765 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.380847 | 干扰表 | 否 |

### [18] 查询2025年每个客户的销售成本和毛利，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_customers`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：75.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.596349 | 真实表-非必需 | 是 |
| 2 | `sales_orders` | 0.567970 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.552499 | 必须召回 | 是 |
| 4 | `dim_products` | 0.530160 | 必须召回 | 是 |
| 5 | `exchange_rates` | 0.527690 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.472187 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.408874 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.391543 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.378681 | 干扰表 | 否 |

### [19] 查询2025年每个客户类型的收入。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_customers`
- 漏召回：`exchange_rates`
- Recall@4：66.7%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.612478 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.587749 | 必须召回 | 是 |
| 3 | `dim_products` | 0.496936 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.489535 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.449668 | 必须召回 | 否 |
| 6 | `hr_attendance_records` | 0.446258 | 干扰表 | 否 |
| 7 | `warehouse_temperature_logs` | 0.441346 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.419183 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.387329 | 干扰表 | 否 |

### [20] 查询2025年每个产品类别的收入和销售成本，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：66.7%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.582973 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.576091 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.559351 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.509307 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.501769 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.438779 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.412614 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.407542 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.339280 | 干扰表 | 否 |

### [21] 查询2025年每个产品线的收入和毛利，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：66.7%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.583858 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.564040 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.525512 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.499939 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.497505 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.471121 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.445325 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.391639 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.333156 | 干扰表 | 否 |

### [22] 查询2025年每个国家的销售收入。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_customers`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.554367 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.493412 | 必须召回 | 是 |
| 3 | `dim_products` | 0.466828 | 真实表-非必需 | 是 |
| 4 | `exchange_rates` | 0.457684 | 必须召回 | 是 |
| 5 | `finance_expenses` | 0.433369 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.406413 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.380559 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.377719 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.310960 | 干扰表 | 否 |

### [23] 查询2025年期间费用总额，期间费用包括研发、销售、管理和财务四项费用。

- 状态：**通过**
- 必须召回：`finance_expenses`
- Top-4 命中：`finance_expenses`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.753348 | 必须召回 | 是 |
| 2 | `dim_products` | 0.603477 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.532850 | 真实表-非必需 | 是 |
| 4 | `dim_customers` | 0.509388 | 真实表-非必需 | 是 |
| 5 | `hr_attendance_records` | 0.480274 | 干扰表 | 否 |
| 6 | `warehouse_temperature_logs` | 0.454690 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.454061 | 干扰表 | 否 |
| 8 | `exchange_rates` | 0.453225 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.441776 | 干扰表 | 否 |

### [24] 查询2025年每个月的期间费用。

- 状态：**通过**
- 必须召回：`finance_expenses`
- Top-4 命中：`finance_expenses`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.617078 | 必须召回 | 是 |
| 2 | `dim_products` | 0.514838 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.481082 | 真实表-非必需 | 是 |
| 4 | `dim_customers` | 0.477972 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.470744 | 真实表-非必需 | 否 |
| 6 | `iot_device_alerts` | 0.453415 | 干扰表 | 否 |
| 7 | `warehouse_temperature_logs` | 0.451992 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.447249 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.401746 | 干扰表 | 否 |

### [25] 查询2025年每个部门的期间费用。

- 状态：**通过**
- 必须召回：`finance_expenses`
- Top-4 命中：`finance_expenses`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.626051 | 必须召回 | 是 |
| 2 | `dim_products` | 0.498159 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.463228 | 真实表-非必需 | 是 |
| 4 | `hr_attendance_records` | 0.458997 | 干扰表 | 是 |
| 5 | `exchange_rates` | 0.437408 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.437397 | 干扰表 | 否 |
| 7 | `dim_customers` | 0.434114 | 真实表-非必需 | 否 |
| 8 | `iot_device_alerts` | 0.417061 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.403972 | 干扰表 | 否 |

### [26] 查询2025年的收入、销售成本和毛利，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.604240 | 真实表-非必需 | 是 |
| 2 | `sales_orders` | 0.555057 | 必须召回 | 是 |
| 3 | `dim_products` | 0.542779 | 必须召回 | 是 |
| 4 | `exchange_rates` | 0.539481 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.516793 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.472859 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.426292 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.416411 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.371415 | 干扰表 | 否 |

### [27] 查询2025年的利润，利润定义为毛利减去四项期间费用，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.659254 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.536342 | 必须召回 | 是 |
| 3 | `dim_products` | 0.501986 | 必须召回 | 是 |
| 4 | `sales_orders` | 0.496159 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.491835 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.467164 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.428336 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.411177 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.368676 | 干扰表 | 否 |

### [28] 查询2025年收入超过100万元的产品，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `exchange_rates` | 0.544388 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.529776 | 必须召回 | 是 |
| 3 | `dim_products` | 0.528721 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.496579 | 真实表-非必需 | 是 |
| 5 | `dim_customers` | 0.482230 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.450375 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.436085 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.431603 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.365026 | 干扰表 | 否 |

### [29] 查询2025年毛利率高于30%的产品，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.571711 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.558705 | 必须召回 | 是 |
| 3 | `finance_expenses` | 0.533539 | 真实表-非必需 | 是 |
| 4 | `sales_orders` | 0.502432 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.497169 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.457761 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.408717 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.375353 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.370971 | 干扰表 | 否 |

### [30] 查询2025年销售数量最多的前10个产品。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`
- Top-4 命中：`sales_orders`, `dim_products`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.495469 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.493066 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.412781 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.368271 | 真实表-非必需 | 是 |
| 5 | `iot_device_alerts` | 0.354321 | 干扰表 | 否 |
| 6 | `hr_attendance_records` | 0.352587 | 干扰表 | 否 |
| 7 | `warehouse_temperature_logs` | 0.347656 | 干扰表 | 否 |
| 8 | `exchange_rates` | 0.323252 | 真实表-非必需 | 否 |
| 9 | `legal_contract_archive` | 0.275051 | 干扰表 | 否 |

### [31] 查询2025年每个月的收入、销售成本、毛利、四项期间费用和利润，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.673926 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.583621 | 必须召回 | 是 |
| 3 | `dim_products` | 0.569986 | 必须召回 | 是 |
| 4 | `exchange_rates` | 0.549677 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.547536 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.502307 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.467133 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.439860 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.404395 | 干扰表 | 否 |

### [32] 查询2025年每个月的收入环比增长率，并显示当月收入和上月收入，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `exchange_rates`
- Top-4 命中：`sales_orders`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `exchange_rates` | 0.530481 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.509752 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.478158 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.472098 | 真实表-非必需 | 是 |
| 5 | `hr_attendance_records` | 0.463192 | 干扰表 | 否 |
| 6 | `dim_products` | 0.455676 | 真实表-非必需 | 否 |
| 7 | `warehouse_temperature_logs` | 0.442201 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.381814 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.314609 | 干扰表 | 否 |

### [33] 查询2025年每个产品类别的收入、销售成本、毛利和毛利率，并按照毛利率从高到低排名，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：66.7%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.626942 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.622590 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.558835 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.537113 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.525238 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.493105 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.418767 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.418611 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.367464 | 干扰表 | 否 |

### [34] 查询2025年每个产品类别收入最高的产品，并显示该产品的收入、成本和毛利，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：66.7%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.598676 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.561552 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.527962 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.485247 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.459609 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.452230 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.417365 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.396136 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.318571 | 干扰表 | 否 |

### [35] 查询2025年每个销售区域收入最高的客户，并显示该客户的收入和毛利，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_customers`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：75.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.579168 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.561998 | 必须召回 | 是 |
| 3 | `finance_expenses` | 0.500725 | 真实表-非必需 | 是 |
| 4 | `dim_products` | 0.491981 | 必须召回 | 是 |
| 5 | `exchange_rates` | 0.486687 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.435473 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.393083 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.367735 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.335878 | 干扰表 | 否 |

### [36] 查询2025年每个客户的收入，并计算该客户收入占公司总收入的比例，只保留收入占比超过5%的客户，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_customers`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.604151 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.591260 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.553840 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.532298 | 真实表-非必需 | 是 |
| 5 | `dim_products` | 0.482591 | 真实表-非必需 | 否 |
| 6 | `hr_attendance_records` | 0.464509 | 干扰表 | 否 |
| 7 | `warehouse_temperature_logs` | 0.456337 | 干扰表 | 否 |
| 8 | `legal_contract_archive` | 0.393995 | 干扰表 | 否 |
| 9 | `iot_device_alerts` | 0.379402 | 干扰表 | 否 |

### [37] 查询2025年每个产品的毛利率，并找出每个产品类别毛利率最高的产品，并换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@4：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.583699 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.526127 | 真实表-非必需 | 是 |
| 3 | `exchange_rates` | 0.501583 | 必须召回 | 是 |
| 4 | `sales_orders` | 0.476869 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.472233 | 真实表-非必需 | 否 |
| 6 | `warehouse_temperature_logs` | 0.451707 | 干扰表 | 否 |
| 7 | `iot_device_alerts` | 0.378978 | 干扰表 | 否 |
| 8 | `hr_attendance_records` | 0.362509 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.324531 | 干扰表 | 否 |

### [38] 查询2025年每个月的利润，并计算利润环比增长率，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- Top-4 命中：`sales_orders`, `exchange_rates`, `finance_expenses`
- 漏召回：`dim_products`
- Recall@4：75.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.539209 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.518785 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.494887 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.493962 | 真实表-非必需 | 是 |
| 5 | `dim_products` | 0.481427 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.466246 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.423600 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.383695 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.338999 | 干扰表 | 否 |

### [39] 查询2025年每个产品类别的收入，并计算每个类别收入占公司总收入的比例，同时按照收入排名，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：66.7%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.566455 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.563038 | 必须召回 | 是 |
| 3 | `finance_expenses` | 0.546820 | 真实表-非必需 | 是 |
| 4 | `dim_customers` | 0.538539 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.510394 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.465896 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.444909 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.414681 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.345603 | 干扰表 | 否 |

### [40] 查询2025年收入最高的10个客户，并显示每个客户的收入、销售成本、毛利、毛利率以及收入排名，并换算成人民币。

- 状态：**漏召回**
- 必须召回：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- Top-4 命中：`sales_orders`, `dim_customers`, `dim_products`
- 漏召回：`exchange_rates`
- Recall@4：75.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.594391 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.586958 | 必须召回 | 是 |
| 3 | `finance_expenses` | 0.548738 | 真实表-非必需 | 是 |
| 4 | `dim_products` | 0.526488 | 必须召回 | 是 |
| 5 | `exchange_rates` | 0.499330 | 必须召回 | 否 |
| 6 | `warehouse_temperature_logs` | 0.448176 | 干扰表 | 否 |
| 7 | `hr_attendance_records` | 0.434523 | 干扰表 | 否 |
| 8 | `iot_device_alerts` | 0.372921 | 干扰表 | 否 |
| 9 | `legal_contract_archive` | 0.355007 | 干扰表 | 否 |

