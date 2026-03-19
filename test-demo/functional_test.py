# -*- coding: utf-8 -*-
"""
功能测试 - 验证各模块核心功能
"""
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001"

class FunctionalTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []

    def login(self):
        resp = self.session.post(f"{BASE_URL}/api/login",
            json={"username": "admin", "password": "admin123"})
        return resp.status_code == 200

    def test(self, module, name, func):
        try:
            status = "PASS" if func() else "FAIL"
        except Exception as e:
            status = "FAIL"
        self.results.append({'module': module, 'name': name, 'status': status})
        icon = "OK" if status == "PASS" else "X"
        print(f"[{icon}] {module} - {name}")

def run_functional_tests():
    t = FunctionalTester()
    if not t.login():
        return []
    # 学员模块
    t.test("学员", "列表查询", lambda: t.session.get(f"{BASE_URL}/api/students").status_code == 200)
    t.test("学员", "分页查询", lambda: t.session.get(f"{BASE_URL}/api/students", params={"page": 1}).status_code == 200)
    # 课程模块
    t.test("课程", "列表查询", lambda: t.session.get(f"{BASE_URL}/api/courses").status_code == 200)
    # 统计模块
    t.test("统计", "仪表盘", lambda: t.session.get(f"{BASE_URL}/api/statistics/dashboard").status_code == 200)
    return t.results

if __name__ == "__main__":
    run_functional_tests()
