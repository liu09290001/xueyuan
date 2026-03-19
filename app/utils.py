# -*- coding: utf-8 -*-
"""
工具类：参数校验、日志、限流、认证
"""
import logging
import time
import jwt
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# JWT密钥（生产环境应从环境变量读取）
import os
JWT_SECRET = os.environ.get('JWT_SECRET', 'xueyuan-jwt-secret-key-2024')
JWT_EXPIRE_HOURS = 24


# ========== 限流器 ==========
class RateLimiter:
    """简单的内存限流器"""
    def __init__(self):
        self.requests = {}  # {ip: [(timestamp, count)]}

    def is_allowed(self, ip, limit=60, window=60):
        """检查是否允许请求，默认每分钟60次"""
        now = time.time()
        if ip not in self.requests:
            self.requests[ip] = []

        # 清理过期记录
        self.requests[ip] = [r for r in self.requests[ip] if now - r[0] < window]

        # 检查请求数
        if len(self.requests[ip]) >= limit:
            return False

        self.requests[ip].append((now, 1))
        return True


rate_limiter = RateLimiter()


# ========== JWT认证 ==========
def generate_token(user_id, username, role='user'):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ========== 装饰器 ==========
def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = request.cookies.get('token', '')
        if not token:
            return jsonify({'code': 40101, 'msg': '请先登录'}), 401
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 40102, 'msg': '登录已过期'}), 401
        g.user_id = payload['user_id']
        g.username = payload['username']
        g.role = payload.get('role', 'user')
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = request.cookies.get('token', '')
        if not token:
            return jsonify({'code': 40101, 'msg': '请先登录'}), 401
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 40102, 'msg': '登录已过期'}), 401
        if payload.get('role') != 'admin':
            return jsonify({'code': 40301, 'msg': '需要管理员权限'}), 403
        g.user_id = payload['user_id']
        g.username = payload['username']
        g.role = payload.get('role', 'user')
        return f(*args, **kwargs)
    return decorated


def rate_limit(limit=60, window=60):
    """限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            if not rate_limiter.is_allowed(ip, limit, window):
                logger.warning(f'限流触发: IP={ip}')
                return jsonify({'code': 42901, 'msg': '请求过于频繁'}), 429
            return f(*args, **kwargs)
        return decorated
    return decorator


# ========== 参数校验 ==========
class Validator:
    """参数校验器"""

    @staticmethod
    def required(data, fields):
        """必填字段校验"""
        missing = [f for f in fields if not data.get(f)]
        if missing:
            return False, f"缺少必填字段: {', '.join(missing)}"
        return True, None

    @staticmethod
    def phone(value):
        """手机号校验"""
        import re
        if value and not re.match(r'^1[3-9]\d{9}$', str(value)):
            return False, "手机号格式不正确"
        return True, None

    @staticmethod
    def length(value, min_len=0, max_len=100, field_name='字段'):
        """长度校验"""
        if value and (len(str(value)) < min_len or len(str(value)) > max_len):
            return False, f"{field_name}长度应在{min_len}-{max_len}之间"
        return True, None
