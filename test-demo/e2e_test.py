# -*- coding: utf-8 -*-
"""
端到端测试 - 模拟完整业务流程
"""
import requests
from datetime import datetime, date

BASE_URL = "http://127.0.0.1:5001"

class E2ETester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []

    def login(self):
        resp = self.session.post(f"{BASE_URL}/api/login",
            json={"username": "admin", "password": "admin123"})
        return resp.status_code == 200

    def run_scenario(self, name, steps_func):
        """运行测试场景"""
        start = datetime.now()
        try:
            steps = steps_func(self)
            duration = (datetime.now() - start).total_seconds()
            self.results.append({'name': name, 'status': 'PASS', 'duration': duration})
            print(f"[OK] {name} ({duration:.2f}s)")
        except Exception as e:
            duration = (datetime.now() - start).total_seconds()
            self.results.append({'name': name, 'status': 'FAIL', 'error': str(e)})
            print(f"[FAIL] {name} - {str(e)}")

def scenario_student_lifecycle(t):
    """学员生命周期测试"""
    # 创建学员
    resp = t.session.post(f"{BASE_URL}/api/students", json={"name": "E2E测试学员"})
    sid = resp.json().get("data", {}).get("id")
    # 更新状态
    t.session.patch(f"{BASE_URL}/api/students/{sid}/status", json={"status": "休学"})
    # 删除
    t.session.delete(f"{BASE_URL}/api/students/{sid}")
    return ["创建", "更新状态", "删除"]

def run_e2e_tests():
    t = E2ETester()
    if not t.login():
        print("登录失败")
        return []
    t.run_scenario("学员生命周期", scenario_student_lifecycle)
    return t.results

if __name__ == "__main__":
    run_e2e_tests()
