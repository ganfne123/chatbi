# Milvus 表召回测试报告

- 运行时间：2026-09-26T17:54:01+08:00
- 测试集：40 条
- 向量模型：`text-embedding-v3`
- Top-K：5
- 真实表：dim_customers, dim_products, sales_orders, finance_expenses, exchange_rates
- 干扰表：dim_employees, hr_attendance, it_assets, office_supplies, website_logs, weather_data

## 汇总指标

| 指标 | 数值 |
|---|---:|
| Mean Recall@K | 100.0% |
| 全部必需表命中率 | 100.0% |
| MRR@K | 0.9750 |
| Top-K 干扰表总数 | 35 |

## 逐表召回率

| 表名 | 必需用例数 | Top-K 命中 | 漏召回 | 召回率 |
|---|---:|---:|---:|---:|
| `dim_customers` | 9 | 9 | 0 | 100.0% |
| `dim_products` | 24 | 24 | 0 | 100.0% |
| `sales_orders` | 31 | 31 | 0 | 100.0% |
| `finance_expenses` | 6 | 6 | 0 | 100.0% |
| `exchange_rates` | 25 | 25 | 0 | 100.0% |

## 逐条结果

### [1] 查询所有客户的客户编号、客户名称、客户类型、所属行业和国家。

- 状态：**通过**
- 必须召回：`dim_customers`
- Top-5 命中：`dim_customers`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.706808 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.635874 | 真实表-非必需 | 是 |
| 3 | `dim_employees` | 0.551857 | 干扰表 | 是 |
| 4 | `hr_attendance` | 0.529942 | 干扰表 | 是 |
| 5 | `website_logs` | 0.527444 | 干扰表 | 是 |
| 6 | `dim_products` | 0.522288 | 真实表-非必需 | 否 |
| 7 | `weather_data` | 0.519392 | 干扰表 | 否 |
| 8 | `office_supplies` | 0.517891 | 干扰表 | 否 |
| 9 | `finance_expenses` | 0.501988 | 真实表-非必需 | 否 |
| 10 | `it_assets` | 0.495485 | 干扰表 | 否 |
| 11 | `exchange_rates` | 0.464033 | 真实表-非必需 | 否 |

### [2] 查询所有产品的产品名称、产品线、类别和技术路线。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-5 命中：`dim_products`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.641987 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.556166 | 真实表-非必需 | 是 |
| 3 | `finance_expenses` | 0.528777 | 真实表-非必需 | 是 |
| 4 | `sales_orders` | 0.528713 | 真实表-非必需 | 是 |
| 5 | `office_supplies` | 0.496772 | 干扰表 | 是 |
| 6 | `it_assets` | 0.485646 | 干扰表 | 否 |
| 7 | `website_logs` | 0.474149 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.473445 | 干扰表 | 否 |
| 9 | `weather_data` | 0.455424 | 干扰表 | 否 |
| 10 | `hr_attendance` | 0.447425 | 干扰表 | 否 |
| 11 | `exchange_rates` | 0.403673 | 真实表-非必需 | 否 |

### [3] 查询所有已完成订单的订单号、客户编号、产品编号、订单日期和订单金额。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-5 命中：`sales_orders`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.743630 | 必须召回 | 是 |
| 2 | `hr_attendance` | 0.590522 | 干扰表 | 是 |
| 3 | `dim_customers` | 0.589689 | 真实表-非必需 | 是 |
| 4 | `office_supplies` | 0.559029 | 干扰表 | 是 |
| 5 | `dim_products` | 0.549593 | 真实表-非必需 | 是 |
| 6 | `website_logs` | 0.546930 | 干扰表 | 否 |
| 7 | `dim_employees` | 0.538625 | 干扰表 | 否 |
| 8 | `finance_expenses` | 0.538300 | 真实表-非必需 | 否 |
| 9 | `it_assets` | 0.483790 | 干扰表 | 否 |
| 10 | `exchange_rates` | 0.480562 | 真实表-非必需 | 否 |
| 11 | `weather_data` | 0.469606 | 干扰表 | 否 |

### [4] 查询每种产品的材料成本和人工成本。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-5 命中：`dim_products`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.660023 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.653154 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.554343 | 真实表-非必需 | 是 |
| 4 | `office_supplies` | 0.550203 | 干扰表 | 是 |
| 5 | `hr_attendance` | 0.512810 | 干扰表 | 是 |
| 6 | `exchange_rates` | 0.509704 | 真实表-非必需 | 否 |
| 7 | `it_assets` | 0.490374 | 干扰表 | 否 |
| 8 | `website_logs` | 0.486676 | 干扰表 | 否 |
| 9 | `dim_customers` | 0.479445 | 真实表-非必需 | 否 |
| 10 | `dim_employees` | 0.473442 | 干扰表 | 否 |
| 11 | `weather_data` | 0.447049 | 干扰表 | 否 |

### [5] 查询每种产品的单位实际成本，实际成本定义为材料成本加人工成本。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-5 命中：`dim_products`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.641225 | 真实表-非必需 | 是 |
| 2 | `dim_products` | 0.622931 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.563987 | 真实表-非必需 | 是 |
| 4 | `office_supplies` | 0.541373 | 干扰表 | 是 |
| 5 | `exchange_rates` | 0.511760 | 真实表-非必需 | 是 |
| 6 | `hr_attendance` | 0.506065 | 干扰表 | 否 |
| 7 | `it_assets` | 0.487032 | 干扰表 | 否 |
| 8 | `website_logs` | 0.484802 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.472125 | 干扰表 | 否 |
| 10 | `dim_customers` | 0.463918 | 真实表-非必需 | 否 |
| 11 | `weather_data` | 0.451720 | 干扰表 | 否 |

### [6] 查询每个国家有多少客户。

- 状态：**通过**
- 必须召回：`dim_customers`
- Top-5 命中：`dim_customers`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.622833 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.568614 | 真实表-非必需 | 是 |
| 3 | `website_logs` | 0.494707 | 干扰表 | 是 |
| 4 | `exchange_rates` | 0.477753 | 真实表-非必需 | 是 |
| 5 | `dim_employees` | 0.477750 | 干扰表 | 是 |
| 6 | `weather_data` | 0.464281 | 干扰表 | 否 |
| 7 | `hr_attendance` | 0.448496 | 干扰表 | 否 |
| 8 | `office_supplies` | 0.434343 | 干扰表 | 否 |
| 9 | `dim_products` | 0.433989 | 真实表-非必需 | 否 |
| 10 | `it_assets` | 0.418498 | 干扰表 | 否 |
| 11 | `finance_expenses` | 0.410015 | 真实表-非必需 | 否 |

### [7] 查询每个产品类别有多少种产品。

- 状态：**通过**
- 必须召回：`dim_products`
- Top-5 命中：`dim_products`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.601414 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.546233 | 真实表-非必需 | 是 |
| 3 | `office_supplies` | 0.523681 | 干扰表 | 是 |
| 4 | `dim_customers` | 0.523481 | 真实表-非必需 | 是 |
| 5 | `finance_expenses` | 0.491230 | 真实表-非必需 | 是 |
| 6 | `exchange_rates` | 0.466471 | 真实表-非必需 | 否 |
| 7 | `dim_employees` | 0.463231 | 干扰表 | 否 |
| 8 | `it_assets` | 0.451359 | 干扰表 | 否 |
| 9 | `hr_attendance` | 0.448891 | 干扰表 | 否 |
| 10 | `website_logs` | 0.438642 | 干扰表 | 否 |
| 11 | `weather_data` | 0.434274 | 干扰表 | 否 |

### [8] 查询已完成订单的总销售数量。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-5 命中：`sales_orders`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.701739 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.541683 | 真实表-非必需 | 是 |
| 3 | `hr_attendance` | 0.516397 | 干扰表 | 是 |
| 4 | `office_supplies` | 0.496893 | 干扰表 | 是 |
| 5 | `website_logs` | 0.483051 | 干扰表 | 是 |
| 6 | `dim_employees` | 0.475961 | 干扰表 | 否 |
| 7 | `dim_products` | 0.474546 | 真实表-非必需 | 否 |
| 8 | `exchange_rates` | 0.469453 | 真实表-非必需 | 否 |
| 9 | `finance_expenses` | 0.444573 | 真实表-非必需 | 否 |
| 10 | `weather_data` | 0.436356 | 干扰表 | 否 |
| 11 | `it_assets` | 0.421225 | 干扰表 | 否 |

### [9] 查询2025年的已完成订单数量。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-5 命中：`sales_orders`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.614682 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.529377 | 真实表-非必需 | 是 |
| 3 | `website_logs` | 0.485760 | 干扰表 | 是 |
| 4 | `office_supplies` | 0.475182 | 干扰表 | 是 |
| 5 | `hr_attendance` | 0.472127 | 干扰表 | 是 |
| 6 | `dim_products` | 0.468442 | 真实表-非必需 | 否 |
| 7 | `exchange_rates` | 0.458443 | 真实表-非必需 | 否 |
| 8 | `dim_employees` | 0.447899 | 干扰表 | 否 |
| 9 | `it_assets` | 0.420093 | 干扰表 | 否 |
| 10 | `finance_expenses` | 0.419385 | 真实表-非必需 | 否 |
| 11 | `weather_data` | 0.406700 | 干扰表 | 否 |

### [10] 查询2025年每个月的已完成订单数量。

- 状态：**通过**
- 必须召回：`sales_orders`
- Top-5 命中：`sales_orders`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.644066 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.545792 | 真实表-非必需 | 是 |
| 3 | `website_logs` | 0.500595 | 干扰表 | 是 |
| 4 | `hr_attendance` | 0.487645 | 干扰表 | 是 |
| 5 | `office_supplies` | 0.478859 | 干扰表 | 是 |
| 6 | `dim_products` | 0.477183 | 真实表-非必需 | 否 |
| 7 | `dim_employees` | 0.471736 | 干扰表 | 否 |
| 8 | `exchange_rates` | 0.463169 | 真实表-非必需 | 否 |
| 9 | `finance_expenses` | 0.458474 | 真实表-非必需 | 否 |
| 10 | `weather_data` | 0.438174 | 干扰表 | 否 |
| 11 | `it_assets` | 0.427863 | 干扰表 | 否 |

### [11] 查询2025年的销售收入，收入按照不含税销售收入计算，并统一换算成人民币。

- 状态：**通过**
- 必须召回：`sales_orders`, `exchange_rates`
- Top-5 命中：`sales_orders`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.609027 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.594064 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.502389 | 真实表-非必需 | 是 |
| 4 | `finance_expenses` | 0.491076 | 真实表-非必需 | 是 |
| 5 | `office_supplies` | 0.472820 | 干扰表 | 是 |
| 6 | `hr_attendance` | 0.468037 | 干扰表 | 否 |
| 7 | `dim_products` | 0.466858 | 真实表-非必需 | 否 |
| 8 | `dim_employees` | 0.460098 | 干扰表 | 否 |
| 9 | `website_logs` | 0.446543 | 干扰表 | 否 |
| 10 | `weather_data` | 0.446298 | 干扰表 | 否 |
| 11 | `it_assets` | 0.431598 | 干扰表 | 否 |

### [12] 查询2025年每个销售区域的收入。

- 状态：**通过**
- 必须召回：`sales_orders`, `exchange_rates`
- Top-5 命中：`sales_orders`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.560989 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.529861 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.522687 | 真实表-非必需 | 是 |
| 4 | `dim_products` | 0.459999 | 真实表-非必需 | 是 |
| 5 | `finance_expenses` | 0.457183 | 真实表-非必需 | 是 |
| 6 | `dim_employees` | 0.429128 | 干扰表 | 否 |
| 7 | `office_supplies` | 0.418273 | 干扰表 | 否 |
| 8 | `hr_attendance` | 0.417910 | 干扰表 | 否 |
| 9 | `website_logs` | 0.409835 | 干扰表 | 否 |
| 10 | `weather_data` | 0.407990 | 干扰表 | 否 |
| 11 | `it_assets` | 0.372719 | 干扰表 | 否 |

### [13] 查询2025年每个产品的销售收入。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.595569 | 必须召回 | 是 |
| 2 | `dim_products` | 0.547068 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.517215 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.510676 | 真实表-非必需 | 是 |
| 5 | `finance_expenses` | 0.490173 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.475121 | 干扰表 | 否 |
| 7 | `website_logs` | 0.447715 | 干扰表 | 否 |
| 8 | `hr_attendance` | 0.435453 | 干扰表 | 否 |
| 9 | `it_assets` | 0.426960 | 干扰表 | 否 |
| 10 | `dim_employees` | 0.419277 | 干扰表 | 否 |
| 11 | `weather_data` | 0.415698 | 干扰表 | 否 |

### [14] 查询2025年每个产品的销售成本，销售成本定义为材料成本加人工成本后乘以销售数量。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`
- Top-5 命中：`sales_orders`, `dim_products`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：2

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.617822 | 真实表-非必需 | 是 |
| 2 | `dim_products` | 0.608384 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.607335 | 必须召回 | 是 |
| 4 | `exchange_rates` | 0.501026 | 真实表-非必需 | 是 |
| 5 | `office_supplies` | 0.487402 | 干扰表 | 是 |
| 6 | `dim_customers` | 0.479348 | 真实表-非必需 | 否 |
| 7 | `hr_attendance` | 0.458217 | 干扰表 | 否 |
| 8 | `it_assets` | 0.428562 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.428172 | 干扰表 | 否 |
| 10 | `website_logs` | 0.420065 | 干扰表 | 否 |
| 11 | `weather_data` | 0.409198 | 干扰表 | 否 |

### [15] 查询2025年每个产品的收入和毛利。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.579048 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.547653 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.534428 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.513087 | 真实表-非必需 | 是 |
| 5 | `dim_customers` | 0.496787 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.467836 | 干扰表 | 否 |
| 7 | `website_logs` | 0.451938 | 干扰表 | 否 |
| 8 | `it_assets` | 0.433224 | 干扰表 | 否 |
| 9 | `hr_attendance` | 0.415744 | 干扰表 | 否 |
| 10 | `dim_employees` | 0.407133 | 干扰表 | 否 |
| 11 | `weather_data` | 0.407020 | 干扰表 | 否 |

### [16] 查询2025年每个产品的毛利率。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.594737 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.515972 | 必须召回 | 是 |
| 3 | `finance_expenses` | 0.502144 | 真实表-非必需 | 是 |
| 4 | `dim_customers` | 0.500751 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.479117 | 必须召回 | 是 |
| 6 | `website_logs` | 0.440874 | 干扰表 | 否 |
| 7 | `weather_data` | 0.426579 | 干扰表 | 否 |
| 8 | `office_supplies` | 0.424696 | 干扰表 | 否 |
| 9 | `it_assets` | 0.422469 | 干扰表 | 否 |
| 10 | `dim_employees` | 0.402140 | 干扰表 | 否 |
| 11 | `hr_attendance` | 0.401525 | 干扰表 | 否 |

### [17] 查询2025年每个客户的销售收入。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_customers`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.625064 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.587533 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.508837 | 必须召回 | 是 |
| 4 | `dim_products` | 0.479457 | 真实表-非必需 | 是 |
| 5 | `website_logs` | 0.469539 | 干扰表 | 是 |
| 6 | `finance_expenses` | 0.468385 | 真实表-非必需 | 否 |
| 7 | `dim_employees` | 0.461356 | 干扰表 | 否 |
| 8 | `hr_attendance` | 0.453897 | 干扰表 | 否 |
| 9 | `office_supplies` | 0.450953 | 干扰表 | 否 |
| 10 | `weather_data` | 0.423004 | 干扰表 | 否 |
| 11 | `it_assets` | 0.414014 | 干扰表 | 否 |

### [18] 查询2025年每个客户的销售成本和毛利。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.578889 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.550298 | 必须召回 | 是 |
| 3 | `dim_products` | 0.538819 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.533118 | 真实表-非必需 | 是 |
| 5 | `exchange_rates` | 0.478357 | 必须召回 | 是 |
| 6 | `website_logs` | 0.445587 | 干扰表 | 否 |
| 7 | `office_supplies` | 0.417920 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.417770 | 干扰表 | 否 |
| 9 | `hr_attendance` | 0.414701 | 干扰表 | 否 |
| 10 | `weather_data` | 0.405241 | 干扰表 | 否 |
| 11 | `it_assets` | 0.382963 | 干扰表 | 否 |

### [19] 查询2025年每个客户类型的收入。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_customers`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.609093 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.587749 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.538073 | 必须召回 | 是 |
| 4 | `website_logs` | 0.488875 | 干扰表 | 是 |
| 5 | `dim_employees` | 0.481861 | 干扰表 | 是 |
| 6 | `dim_products` | 0.478590 | 真实表-非必需 | 否 |
| 7 | `finance_expenses` | 0.469392 | 真实表-非必需 | 否 |
| 8 | `office_supplies` | 0.455708 | 干扰表 | 否 |
| 9 | `hr_attendance` | 0.446065 | 干扰表 | 否 |
| 10 | `weather_data` | 0.441079 | 干扰表 | 否 |
| 11 | `it_assets` | 0.421065 | 干扰表 | 否 |

### [20] 查询2025年每个产品类别的收入和销售成本。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.610634 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.565085 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.562265 | 必须召回 | 是 |
| 4 | `exchange_rates` | 0.524139 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.501348 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.457660 | 干扰表 | 否 |
| 7 | `website_logs` | 0.417567 | 干扰表 | 否 |
| 8 | `hr_attendance` | 0.406691 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.402927 | 干扰表 | 否 |
| 10 | `weather_data` | 0.389337 | 干扰表 | 否 |
| 11 | `it_assets` | 0.384579 | 干扰表 | 否 |

### [21] 查询2025年每个产品线的收入和毛利。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.581356 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.526029 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.510755 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.500818 | 真实表-非必需 | 是 |
| 5 | `dim_customers` | 0.490105 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.422544 | 干扰表 | 否 |
| 7 | `website_logs` | 0.421312 | 干扰表 | 否 |
| 8 | `it_assets` | 0.405101 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.396438 | 干扰表 | 否 |
| 10 | `hr_attendance` | 0.387555 | 干扰表 | 否 |
| 11 | `weather_data` | 0.375555 | 干扰表 | 否 |

### [22] 查询2025年每个国家的销售收入。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_customers`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.554367 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.503293 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.490781 | 必须召回 | 是 |
| 4 | `dim_products` | 0.442924 | 真实表-非必需 | 是 |
| 5 | `finance_expenses` | 0.427003 | 真实表-非必需 | 是 |
| 6 | `weather_data` | 0.403560 | 干扰表 | 否 |
| 7 | `website_logs` | 0.400722 | 干扰表 | 否 |
| 8 | `office_supplies` | 0.388704 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.383387 | 干扰表 | 否 |
| 10 | `hr_attendance` | 0.378847 | 干扰表 | 否 |
| 11 | `it_assets` | 0.355772 | 干扰表 | 否 |

### [23] 查询2025年期间费用总额，期间费用包括研发、销售、管理和财务四项费用。

- 状态：**通过**
- 必须召回：`finance_expenses`
- Top-5 命中：`finance_expenses`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.753104 | 必须召回 | 是 |
| 2 | `dim_products` | 0.631247 | 真实表-非必需 | 是 |
| 3 | `exchange_rates` | 0.535317 | 真实表-非必需 | 是 |
| 4 | `sales_orders` | 0.532850 | 真实表-非必需 | 是 |
| 5 | `office_supplies` | 0.519306 | 干扰表 | 是 |
| 6 | `dim_customers` | 0.508168 | 真实表-非必需 | 否 |
| 7 | `hr_attendance` | 0.493286 | 干扰表 | 否 |
| 8 | `it_assets` | 0.491397 | 干扰表 | 否 |
| 9 | `website_logs` | 0.468029 | 干扰表 | 否 |
| 10 | `dim_employees` | 0.460074 | 干扰表 | 否 |
| 11 | `weather_data` | 0.407642 | 干扰表 | 否 |

### [24] 查询2025年每个月的期间费用。

- 状态：**通过**
- 必须召回：`finance_expenses`
- Top-5 命中：`finance_expenses`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.596621 | 必须召回 | 是 |
| 2 | `dim_products` | 0.518739 | 真实表-非必需 | 是 |
| 3 | `exchange_rates` | 0.505423 | 真实表-非必需 | 是 |
| 4 | `sales_orders` | 0.481082 | 真实表-非必需 | 是 |
| 5 | `dim_customers` | 0.477408 | 真实表-非必需 | 是 |
| 6 | `website_logs` | 0.466487 | 干扰表 | 否 |
| 7 | `hr_attendance` | 0.453730 | 干扰表 | 否 |
| 8 | `office_supplies` | 0.441511 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.426022 | 干扰表 | 否 |
| 10 | `weather_data` | 0.425091 | 干扰表 | 否 |
| 11 | `it_assets` | 0.423847 | 干扰表 | 否 |

### [25] 查询2025年每个部门的期间费用。

- 状态：**通过**
- 必须召回：`finance_expenses`
- Top-5 命中：`finance_expenses`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.633163 | 必须召回 | 是 |
| 2 | `dim_products` | 0.520338 | 真实表-非必需 | 是 |
| 3 | `office_supplies` | 0.485076 | 干扰表 | 是 |
| 4 | `exchange_rates` | 0.470055 | 真实表-非必需 | 是 |
| 5 | `hr_attendance` | 0.467021 | 干扰表 | 是 |
| 6 | `sales_orders` | 0.463228 | 真实表-非必需 | 否 |
| 7 | `website_logs` | 0.437831 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.436061 | 干扰表 | 否 |
| 9 | `dim_customers` | 0.433714 | 真实表-非必需 | 否 |
| 10 | `weather_data` | 0.414786 | 干扰表 | 否 |
| 11 | `it_assets` | 0.408789 | 干扰表 | 否 |

### [26] 查询2025年的收入、销售成本和毛利。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.566685 | 必须召回 | 是 |
| 2 | `dim_products` | 0.563319 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.558741 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.545035 | 真实表-非必需 | 是 |
| 5 | `dim_customers` | 0.514493 | 真实表-非必需 | 是 |
| 6 | `website_logs` | 0.461053 | 干扰表 | 否 |
| 7 | `office_supplies` | 0.439200 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.432553 | 干扰表 | 否 |
| 9 | `hr_attendance` | 0.431078 | 干扰表 | 否 |
| 10 | `it_assets` | 0.420752 | 干扰表 | 否 |
| 11 | `weather_data` | 0.415298 | 干扰表 | 否 |

### [27] 查询2025年的利润，利润定义为毛利减去四项期间费用。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.576235 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.551108 | 必须召回 | 是 |
| 3 | `dim_products` | 0.533569 | 必须召回 | 是 |
| 4 | `sales_orders` | 0.492415 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.490731 | 真实表-非必需 | 是 |
| 6 | `hr_attendance` | 0.435528 | 干扰表 | 否 |
| 7 | `website_logs` | 0.433436 | 干扰表 | 否 |
| 8 | `it_assets` | 0.430543 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.414811 | 干扰表 | 否 |
| 10 | `office_supplies` | 0.414132 | 干扰表 | 否 |
| 11 | `weather_data` | 0.397255 | 干扰表 | 否 |

### [28] 查询2025年收入超过100万元的产品。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `exchange_rates` | 0.565749 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.519508 | 必须召回 | 是 |
| 3 | `dim_products` | 0.513777 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.468981 | 真实表-非必需 | 是 |
| 5 | `office_supplies` | 0.458395 | 干扰表 | 是 |
| 6 | `finance_expenses` | 0.451365 | 真实表-非必需 | 否 |
| 7 | `website_logs` | 0.439299 | 干扰表 | 否 |
| 8 | `hr_attendance` | 0.428998 | 干扰表 | 否 |
| 9 | `it_assets` | 0.425754 | 干扰表 | 否 |
| 10 | `dim_employees` | 0.405743 | 干扰表 | 否 |
| 11 | `weather_data` | 0.369407 | 干扰表 | 否 |

### [29] 查询2025年毛利率高于30%的产品。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.561663 | 必须召回 | 是 |
| 2 | `exchange_rates` | 0.500382 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.496724 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.495665 | 真实表-非必需 | 是 |
| 5 | `finance_expenses` | 0.463259 | 真实表-非必需 | 是 |
| 6 | `it_assets` | 0.411629 | 干扰表 | 否 |
| 7 | `website_logs` | 0.408568 | 干扰表 | 否 |
| 8 | `weather_data` | 0.401973 | 干扰表 | 否 |
| 9 | `office_supplies` | 0.391391 | 干扰表 | 否 |
| 10 | `dim_employees` | 0.389579 | 干扰表 | 否 |
| 11 | `hr_attendance` | 0.380620 | 干扰表 | 否 |

### [30] 查询2025年销售数量最多的前10个产品。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`
- Top-5 命中：`sales_orders`, `dim_products`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.493066 | 必须召回 | 是 |
| 2 | `dim_products` | 0.461779 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.419382 | 真实表-非必需 | 是 |
| 4 | `dim_customers` | 0.412456 | 真实表-非必需 | 是 |
| 5 | `office_supplies` | 0.401336 | 干扰表 | 是 |
| 6 | `finance_expenses` | 0.353592 | 真实表-非必需 | 否 |
| 7 | `it_assets` | 0.347564 | 干扰表 | 否 |
| 8 | `website_logs` | 0.346268 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.344575 | 干扰表 | 否 |
| 10 | `hr_attendance` | 0.343221 | 干扰表 | 否 |
| 11 | `weather_data` | 0.336553 | 干扰表 | 否 |

### [31] 查询2025年每个月的收入、销售成本、毛利、四项期间费用和利润。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `finance_expenses` | 0.633229 | 必须召回 | 是 |
| 2 | `dim_products` | 0.602447 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.599056 | 必须召回 | 是 |
| 4 | `exchange_rates` | 0.562212 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.555208 | 真实表-非必需 | 是 |
| 6 | `website_logs` | 0.494560 | 干扰表 | 否 |
| 7 | `hr_attendance` | 0.481617 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.476723 | 干扰表 | 否 |
| 9 | `office_supplies` | 0.475005 | 干扰表 | 否 |
| 10 | `it_assets` | 0.461905 | 干扰表 | 否 |
| 11 | `weather_data` | 0.453310 | 干扰表 | 否 |

### [32] 查询2025年每个月的收入环比增长率，并显示当月收入和上月收入。

- 状态：**通过**
- 必须召回：`sales_orders`, `exchange_rates`
- Top-5 命中：`sales_orders`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `exchange_rates` | 0.608122 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.514637 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.478553 | 真实表-非必需 | 是 |
| 4 | `website_logs` | 0.468836 | 干扰表 | 是 |
| 5 | `finance_expenses` | 0.467759 | 真实表-非必需 | 是 |
| 6 | `dim_employees` | 0.462741 | 干扰表 | 否 |
| 7 | `hr_attendance` | 0.460296 | 干扰表 | 否 |
| 8 | `dim_products` | 0.446211 | 真实表-非必需 | 否 |
| 9 | `weather_data` | 0.427892 | 干扰表 | 否 |
| 10 | `office_supplies` | 0.396453 | 干扰表 | 否 |
| 11 | `it_assets` | 0.380213 | 干扰表 | 否 |

### [33] 查询2025年每个产品类别的收入、销售成本、毛利和毛利率，并按照毛利率从高到低排名。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.636764 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.549646 | 真实表-非必需 | 是 |
| 3 | `sales_orders` | 0.546955 | 必须召回 | 是 |
| 4 | `exchange_rates` | 0.530028 | 必须召回 | 是 |
| 5 | `dim_customers` | 0.523884 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.446219 | 干扰表 | 否 |
| 7 | `website_logs` | 0.434127 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.423323 | 干扰表 | 否 |
| 9 | `weather_data` | 0.409091 | 干扰表 | 否 |
| 10 | `hr_attendance` | 0.405010 | 干扰表 | 否 |
| 11 | `it_assets` | 0.396701 | 干扰表 | 否 |

### [34] 查询2025年每个产品类别收入最高的产品，并显示该产品的收入、成本和毛利。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.602292 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.529803 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.524919 | 必须召回 | 是 |
| 4 | `finance_expenses` | 0.507691 | 真实表-非必需 | 是 |
| 5 | `dim_customers` | 0.479875 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.441584 | 干扰表 | 否 |
| 7 | `website_logs` | 0.406141 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.383668 | 干扰表 | 否 |
| 9 | `hr_attendance` | 0.381658 | 干扰表 | 否 |
| 10 | `it_assets` | 0.371859 | 干扰表 | 否 |
| 11 | `weather_data` | 0.361725 | 干扰表 | 否 |

### [35] 查询2025年每个销售区域收入最高的客户，并显示该客户的收入和毛利。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.572426 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.554490 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.502263 | 必须召回 | 是 |
| 4 | `dim_products` | 0.445535 | 必须召回 | 是 |
| 5 | `dim_employees` | 0.417944 | 干扰表 | 是 |
| 6 | `finance_expenses` | 0.416404 | 真实表-非必需 | 否 |
| 7 | `website_logs` | 0.392960 | 干扰表 | 否 |
| 8 | `hr_attendance` | 0.377965 | 干扰表 | 否 |
| 9 | `weather_data` | 0.371790 | 干扰表 | 否 |
| 10 | `office_supplies` | 0.357355 | 干扰表 | 否 |
| 11 | `it_assets` | 0.318004 | 干扰表 | 否 |

### [36] 查询2025年每个客户的收入，并计算该客户收入占公司总收入的比例，只保留收入占比超过5%的客户。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_customers`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_customers` | 0.601890 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.580868 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.561321 | 必须召回 | 是 |
| 4 | `website_logs` | 0.483971 | 干扰表 | 是 |
| 5 | `dim_employees` | 0.482950 | 干扰表 | 是 |
| 6 | `finance_expenses` | 0.482156 | 真实表-非必需 | 否 |
| 7 | `dim_products` | 0.474760 | 真实表-非必需 | 否 |
| 8 | `hr_attendance` | 0.464076 | 干扰表 | 否 |
| 9 | `office_supplies` | 0.448073 | 干扰表 | 否 |
| 10 | `weather_data` | 0.427119 | 干扰表 | 否 |
| 11 | `it_assets` | 0.420962 | 干扰表 | 否 |

### [37] 查询2025年每个产品的毛利率，并找出每个产品类别毛利率最高的产品。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `dim_products` | 0.573465 | 必须召回 | 是 |
| 2 | `sales_orders` | 0.471976 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.468425 | 真实表-非必需 | 是 |
| 4 | `exchange_rates` | 0.463907 | 必须召回 | 是 |
| 5 | `finance_expenses` | 0.459054 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.382578 | 干扰表 | 否 |
| 7 | `weather_data` | 0.376073 | 干扰表 | 否 |
| 8 | `website_logs` | 0.373013 | 干扰表 | 否 |
| 9 | `dim_employees` | 0.366233 | 干扰表 | 否 |
| 10 | `it_assets` | 0.361625 | 干扰表 | 否 |
| 11 | `hr_attendance` | 0.353848 | 干扰表 | 否 |

### [38] 查询2025年每个月的利润，并计算利润环比增长率。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`, `finance_expenses`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `exchange_rates` | 0.540563 | 必须召回 | 是 |
| 2 | `finance_expenses` | 0.494661 | 必须召回 | 是 |
| 3 | `dim_customers` | 0.486996 | 真实表-非必需 | 是 |
| 4 | `sales_orders` | 0.486446 | 必须召回 | 是 |
| 5 | `dim_products` | 0.479259 | 必须召回 | 是 |
| 6 | `website_logs` | 0.421199 | 干扰表 | 否 |
| 7 | `hr_attendance` | 0.416088 | 干扰表 | 否 |
| 8 | `dim_employees` | 0.412244 | 干扰表 | 否 |
| 9 | `weather_data` | 0.405541 | 干扰表 | 否 |
| 10 | `it_assets` | 0.383412 | 干扰表 | 否 |
| 11 | `office_supplies` | 0.330079 | 干扰表 | 否 |

### [39] 查询2025年每个产品类别的收入，并计算每个类别收入占公司总收入的比例，同时按照收入排名。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `exchange_rates` | 0.583313 | 必须召回 | 是 |
| 2 | `dim_products` | 0.569683 | 必须召回 | 是 |
| 3 | `sales_orders` | 0.557600 | 必须召回 | 是 |
| 4 | `dim_customers` | 0.534142 | 真实表-非必需 | 是 |
| 5 | `finance_expenses` | 0.517627 | 真实表-非必需 | 是 |
| 6 | `office_supplies` | 0.473932 | 干扰表 | 否 |
| 7 | `dim_employees` | 0.441734 | 干扰表 | 否 |
| 8 | `website_logs` | 0.434203 | 干扰表 | 否 |
| 9 | `hr_attendance` | 0.434013 | 干扰表 | 否 |
| 10 | `weather_data` | 0.400011 | 干扰表 | 否 |
| 11 | `it_assets` | 0.395572 | 干扰表 | 否 |

### [40] 查询2025年收入最高的10个客户，并显示每个客户的收入、销售成本、毛利、毛利率以及收入排名。

- 状态：**通过**
- 必须召回：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- Top-5 命中：`sales_orders`, `dim_customers`, `dim_products`, `exchange_rates`
- 漏召回：无
- Recall@5：100.0%
- 首个必需表排名：1

| 排名 | 表名 | 得分 | 类型 | Top-K |
|---:|---|---:|---|---|
| 1 | `sales_orders` | 0.599794 | 必须召回 | 是 |
| 2 | `dim_customers` | 0.594586 | 必须召回 | 是 |
| 3 | `exchange_rates` | 0.521022 | 必须召回 | 是 |
| 4 | `dim_products` | 0.512989 | 必须召回 | 是 |
| 5 | `finance_expenses` | 0.482735 | 真实表-非必需 | 是 |
| 6 | `dim_employees` | 0.475094 | 干扰表 | 否 |
| 7 | `website_logs` | 0.472697 | 干扰表 | 否 |
| 8 | `hr_attendance` | 0.438125 | 干扰表 | 否 |
| 9 | `office_supplies` | 0.419417 | 干扰表 | 否 |
| 10 | `weather_data` | 0.406970 | 干扰表 | 否 |
| 11 | `it_assets` | 0.389281 | 干扰表 | 否 |

