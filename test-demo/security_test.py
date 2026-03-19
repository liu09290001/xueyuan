# -*- coding: utf-8 -*-
"""
安全测试 - 验证认证、授权和安全防护
"""
import requests

BASE_URL = "http://127.0.0.1:5001"

class SecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []

    def test(self, category, name, func):
        try:
            status = "PASS" if func() else "FAIL"
        except:
            status = "FAIL"
        self.results.append({'category': category, 'name': name, 'status': status})
        icon = "OK" if status == "PASS" else "X"
        print(f"[{icon}] {category} - {name}")

def run_security_tests():
    t = SecurityTester()
    # 认证测试
    t.test("认证", "未登录拒绝", lambda: requests.get(f"{BASE_URL}/api/students").status_code == 401)
    t.test("认证", "错误密码拒绝", lambda: requests.post(f"{BASE_URL}/api/login", json={"username": "admin", "password": "wrong"}).status_code == 401)
    return t.results

if __name__ == "__main__":
    run_security_tests()
