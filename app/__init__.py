# -*- coding: utf-8 -*-
"""
Flask应用初始化
"""
import os
from flask import Flask, jsonify
from app.models import db, User


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)

    # 配置（生产环境应从环境变量读取）
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xueyuan-system-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///xueyuan.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from app.routes import register_blueprints
    register_blueprints(app)

    # 全局异常处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'code': 40401, 'msg': '资源不存在'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'code': 50001, 'msg': '服务器内部错误'}), 500

    # 创建数据库表和初始化管理员
    with app.app_context():
        db.create_all()
        # 初始化管理员账号
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    return app
