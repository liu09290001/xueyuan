# 测试用例执行指南

## 目录结构

```
testcases/
├── api/                    # API测试用例CSV
├── e2e/                    # E2E测试用例CSV
├── security/               # 安全测试用例CSV
├── performance/            # 性能测试用例CSV
├── boundary/               # 边界值测试用例CSV
├── exception/              # 异常测试用例CSV
├── ui/                     # UI测试用例CSV
├── smoke/                  # 冒烟测试用例CSV
├── run_api_tests.py        # API测试执行脚本
├── run_e2e_tests.py        # E2E测试执行脚本
├── run_security_tests.py   # 安全测试执行脚本
├── run_performance_tests.py # 性能测试执行脚本
├── run_all_tests.py        # 统一执行脚本
└── README.md               # 本文档
```

## 快速开始

### 1. 环境准备

```bash
pip install requests
```

### 2. 启动服务

```bash
cd D:\Claude-test\xueyuan-test
python run.py
```

### 3. 执行测试

**执行所有测试:**
```bash
cd test/testcases
python run_all_tests.py
```

**执行单类测试:**
```bash
python run_api_tests.py        # API测试
python run_e2e_tests.py        # E2E测试
python run_security_tests.py   # 安全测试
python run_performance_tests.py # 性能测试
```

## 测试用例统计

| 类型 | 用例数 | 自动化率 |
|------|--------|---------|
| API测试 | 107 | 100% |
| E2E测试 | 40 | 100% |
| 安全测试 | 33 | 97% |
| 性能测试 | 6 | 100% |
| 边界值测试 | 12 | 100% |
| 异常测试 | 10 | 100% |
| UI测试 | 4 | 100% |
| 冒烟测试 | 5 | 100% |
| **总计** | **217** | **99%** |

## 测试报告

执行后会生成测试报告:
- `api_test_report.md` - API测试报告

## 注意事项

1. 确保服务已启动(http://localhost:5000)
2. 默认使用admin/admin123登录
3. 测试会创建/修改/删除数据,建议使用测试数据库
