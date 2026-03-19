# CLAUDE.md

本文件为 Claude Code 在此代码库中工作时提供指导。

## 系统概述

这是一个基于 Web 的学员管理系统，采用 Flask REST API 后端和原生 JavaScript 前端。系统管理学员、课程、报名缴费、考勤，并具有基于 Session/Cookie 的用户认证和访问控制功能。

## 技术栈

- 后端：Python 3.11 + Flask 3.0 + Flask-SQLAlchemy
- 数据库：SQLite（文件：instance/xueyuan.db）
- 前端：Bootstrap 5 + jQuery + Chart.js
- 认证：JWT Token（存储于 Cookie）

## 项目结构

```
xueyuan-test/
├── app/
│   ├── __init__.py      # Flask 应用工厂
│   ├── models.py        # SQLAlchemy 数据模型
│   ├── routes.py        # API 路由和页面路由
│   ├── utils.py         # 工具函数（认证、日志、限流）
│   ├── templates/       # Jinja2 模板
│   └── static/          # 静态资源（CSS/JS/字体）
├── test/
│   ├── api_test.py      # API 自动化测试
│   ├── functional/      # 功能测试用例 CSV
│   ├── api/             # 接口测试用例 CSV
│   └── reports/         # 测试报告输出
├── instance/
│   └── xueyuan.db       # SQLite 数据库文件
├── run.py               # 应用启动入口
├── requirements.txt     # Python 依赖
└── seed_data.py         # 测试数据生成脚本
```

## 数据模型

| 模型 | 表名 | 说明 |
|------|------|------|
| User | users | 系统用户（admin/user 角色） |
| Student | students | 学员信息 |
| Course | courses | 课程信息 |
| Enrollment | enrollments | 报名记录（关联学员和课程） |
| Payment | payments | 缴费记录（关联报名） |
| Attendance | attendances | 考勤记录 |

关键关联：
- Student 1:N Enrollment N:1 Course
- Enrollment 1:N Payment
- Student/Course 1:N Attendance

## API 接口规范

基础路径：`/api`

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /login | 用户登录 |
| POST | /logout | 用户登出 |

### 学员接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /students | 获取学员列表（支持分页、筛选） |
| POST | /students | 新增学员 |
| GET | /students/:id | 获取学员详情 |
| PUT | /students/:id | 更新学员信息 |
| PATCH | /students/:id/status | 更新学员状态 |
| DELETE | /students/:id | 删除学员 |

### 课程接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /courses | 获取课程列表 |
| POST | /courses | 新增课程 |
| GET | /courses/:id | 获取课程详情 |
| PUT | /courses/:id | 更新课程 |
| DELETE | /courses/:id | 删除课程 |

### 报名缴费接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /enrollments | 获取报名列表 |
| POST | /enrollments | 新增报名 |
| DELETE | /enrollments/:id | 删除报名 |
| POST | /payments | 新增缴费记录 |

### 考勤接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /attendances | 获取考勤记录 |
| POST | /attendances | 记录考勤 |

### 统计接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /statistics/dashboard | 仪表盘数据 |
| GET | /statistics/charts | 图表统计数据 |

## 常用命令

```bash
# 启动开发服务器
python run.py

# 生成测试数据
python seed_data.py

# 运行 API 测试
python test/api_test.py
```

## 开发规范

### 代码风格
- Python 代码遵循 PEP 8
- 所有注释使用中文
- API 返回格式：`{"code": 0, "msg": "success", "data": {...}}`

### 错误码规范
| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 40001 | 参数错误 |
| 40101 | 认证失败 |
| 40401 | 资源不存在 |
| 40901 | 资源冲突 |
| 50001 | 服务器错误 |

### 删除约束
- 学员有报名记录时不可删除
- 课程有报名记录时不可删除
- 删除报名会级联删除缴费记录

## 默认账号

- 用户名：admin
- 密码：admin123

## 注意事项

1. 所有 API（除登录/登出）需要认证，未登录返回 401
2. 分页参数：page（页码）、per_page（每页条数，默认10）
3. 静态资源已本地化，无需外网访问
4. 数据库文件位于 instance/xueyuan.db，首次运行自动创建
