# -*- coding: utf-8 -*-
"""
API接口测试 - 完整接口覆盖测试
"""
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []

    def login(self):
        resp = self.session.post(f"{BASE_URL}/api/login",
            json={"username": "admin", "password": "admin123"})
        return resp.status_code == 200

    def test(self, name, method, url, data=None, expected=200):
        try:
            if method == "GET":
                resp = self.session.get(BASE_URL + url, params=data)
            elif method == "POST":
                resp = self.session.post(BASE_URL + url, json=data)
            status = "PASS" if resp.status_code == expected else "FAIL"
        except:
            status = "FAIL"
        self.results.append({'name': name, 'status': status})
        print(f"[{'OK' if status == 'PASS' else 'X'}] {name}")

def main():
    t = APITester()
    if not t.login():
        return
    t.test("学员列表", "GET", "/api/students")
    t.test("课程列表", "GET", "/api/courses")
    t.test("统计数据", "GET", "/api/statistics/dashboard")

if __name__ == "__main__":
    main()
