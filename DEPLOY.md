# 学员管理系统部署指南

## 环境要求

- Python 3.9+
- pip 包管理器
- 操作系统：Windows / Linux / macOS

## 快速部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd xueyuan-test
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动应用

```bash
python run.py
```

应用默认运行在 http://127.0.0.1:5001

### 5. 初始化测试数据（可选）

```bash
python seed_data.py
```

## 生产环境部署

### 使用 Gunicorn（Linux）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app()"
```

### 使用 Waitress（Windows）

```bash
pip install waitress
waitress-serve --port=5001 app:create_app
```

### Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Systemd 服务配置（Linux）

创建 `/etc/systemd/system/xueyuan.service`：

```ini
[Unit]
Description=Xueyuan Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/xueyuan-test
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable xueyuan
sudo systemctl start xueyuan
```

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
EXPOSE 5001
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:create_app()"]
```

### 构建和运行

```bash
docker build -t xueyuan-system .
docker run -d -p 5001:5001 -v xueyuan-data:/app/instance xueyuan-system
```

## 数据库备份

```bash
# 备份
cp instance/xueyuan.db instance/xueyuan_backup_$(date +%Y%m%d).db

# 恢复
cp instance/xueyuan_backup_20260225.db instance/xueyuan.db
```

## 运行测试

```bash
# 运行 API 自动化测试
python test/api_test.py

# 测试报告输出到 test/reports/ 目录
```

## 常见问题

### 端口被占用

```bash
# 查看端口占用
netstat -ano | findstr :5001

# 修改端口：编辑 run.py 中的 port 参数
```

### 数据库文件不存在

首次运行会自动创建 `instance/xueyuan.db`，无需手动操作。

### 静态资源加载慢

本项目已将所有静态资源本地化，无需外网访问。

## 默认账号

- 用户名：admin
- 密码：admin123
