# -*- coding: utf-8 -*-
"""
学员管理系统启动入口
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print('学员管理系统启动中...')
    print('访问地址: http://127.0.0.1:5001')
    app.run(debug=True, host='127.0.0.1', port=5001)
