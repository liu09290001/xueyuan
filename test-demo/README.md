n# 学员管理系统测试用例

## 概述

本目录包含学员管理系统的完整测试用例，覆盖功能测试、接口测试和性能测试。

## 目录结构

```
test/
├── functional/           # 功能测试用例
├── api/                  # 接口测试用例
├── performance/          # 性能测试方案
└── README.md
```

## 测试用例统计

| 类型 | 文件数 | 用例数 |
|------|--------|--------|
| 功能测试 | 5 | 57 |
| 接口测试 | 5 | 46 |
| 性能测试 | 1 | 15 |
| 合计 | 11 | 118 |

## 功能测试用例

| 文件 | 模块 | 用例数 |
|------|------|--------|
| student_test.csv | 学员管理 | 15 |
| course_test.csv | 课程管理 | 12 |
| enrollment_test.csv | 报名缴费 | 12 |
| attendance_test.csv | 考勤管理 | 10 |
| statistics_test.csv | 数据统计 | 8 |

## 接口测试用例

| 文件 | 模块 | 用例数 |
|------|------|--------|
| student_api_test.csv | 学员接口 | 12 |
| course_api_test.csv | 课程接口 | 10 |
| enrollment_api_test.csv | 报名缴费接口 | 10 |
| attendance_api_test.csv | 考勤接口 | 8 |
| statistics_api_test.csv | 统计接口 | 6 |

## 使用说明

CSV 文件可直接用 Excel 打开编辑，或导入测试管理工具（如 TestLink、禅道）。

