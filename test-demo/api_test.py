# -*- coding: utf-8 -*-
"""
API接口测试框架 - 完整版
根据测试策略文档覆盖：认证、学员、课程、报名缴费、考勤、统计
测试类型：功能测试、接口测试、安全测试、边界值测试
"""
import requests
import json
import os
from datetime import datetime, date, timedelta

BASE_URL = "http://127.0.0.1:5001"
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")


class TestResult:
    """测试结果类"""
    def __init__(self, case_id, name, module, method, url):
        self.case_id = case_id
        self.name = name
        self.module = module
        self.method = method
        self.url = url
        self.status = "PENDING"
        self.expected_code = 200
        self.actual_code = 0
        self.response = None
        self.error = None
        self.duration = 0


class APITester:
    """API测试器"""
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.case_counter = 0
        self.start_time = datetime.now()

    def login(self, username="admin", password="admin123"):
        """登录"""
        resp = self.session.post(f"{BASE_URL}/api/login",
            json={"username": username, "password": password})
        return resp.status_code == 200, resp

    def logout(self):
        """登出"""
        return self.session.post(f"{BASE_URL}/api/logout")

    def run_test(self, name, module, method, url, data=None, expected=200):
        """执行测试用例"""
        self.case_counter += 1
        result = TestResult(self.case_counter, name, module, method, url)
        result.expected_code = expected

        start = datetime.now()
        try:
            full_url = BASE_URL + url
            if method == "GET":
                resp = self.session.get(full_url, params=data)
            elif method == "POST":
                resp = self.session.post(full_url, json=data)
            elif method == "PUT":
                resp = self.session.put(full_url, json=data)
            elif method == "PATCH":
                resp = self.session.patch(full_url, json=data)
            elif method == "DELETE":
                resp = self.session.delete(full_url)
            else:
                raise ValueError(f"Unsupported method: {method}")

            result.actual_code = resp.status_code
            result.response = resp.json() if resp.text else {}
            result.status = "PASS" if resp.status_code == expected else "FAIL"
        except Exception as e:
            result.status = "ERROR"
            result.error = str(e)

        result.duration = (datetime.now() - start).total_seconds() * 1000
        self.results.append(result)

        icon = "OK" if result.status == "PASS" else "X"
        print(f"  [{icon}] {name} ({result.duration:.0f}ms)")
        if result.status != "PASS":
            print(f"      Expected: {expected}, Actual: {result.actual_code}")

        return result.response or {}

    def get_stats(self):
        """统计结果"""
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        error = len([r for r in self.results if r.status == "ERROR"])
        return {"total": len(self.results), "passed": passed, "failed": failed, "error": error}


def generate_html_report(tester, filename):
    """生成HTML测试报告"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    stats = tester.get_stats()
    duration = (datetime.now() - tester.start_time).total_seconds()
    pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>API测试报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4f46e5; padding-bottom: 10px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ flex: 1; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.total {{ background: #e0e7ff; color: #3730a3; }}
        .stat-card.pass {{ background: #d1fae5; color: #065f46; }}
        .stat-card.fail {{ background: #fee2e2; color: #991b1b; }}
        .stat-card.error {{ background: #fef3c7; color: #92400e; }}
        .stat-card h2 {{ margin: 0; font-size: 36px; }}
        .stat-card p {{ margin: 5px 0 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        tr:hover {{ background: #f9fafb; }}
        .badge {{ padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .badge.pass {{ background: #d1fae5; color: #065f46; }}
        .badge.fail {{ background: #fee2e2; color: #991b1b; }}
        .badge.error {{ background: #fef3c7; color: #92400e; }}
        .info {{ color: #6b7280; font-size: 14px; margin: 10px 0; }}
    </style>
</head>
<body>
<div class="container">
    <h1>API测试报告</h1>
    <p class="info">执行时间: {tester.start_time.strftime("%Y-%m-%d %H:%M:%S")} | 耗时: {duration:.2f}秒 | 通过率: {pass_rate:.1f}%</p>
    <div class="summary">
        <div class="stat-card total"><h2>{stats["total"]}</h2><p>总用例</p></div>
        <div class="stat-card pass"><h2>{stats["passed"]}</h2><p>通过</p></div>
        <div class="stat-card fail"><h2>{stats["failed"]}</h2><p>失败</p></div>
        <div class="stat-card error"><h2>{stats["error"]}</h2><p>错误</p></div>
    </div>
    <table>
        <thead><tr><th>序号</th><th>模块</th><th>用例名称</th><th>方法</th><th>接口</th><th>预期</th><th>实际</th><th>耗时</th><th>结果</th></tr></thead>
        <tbody>
'''
    for r in tester.results:
        badge_class = r.status.lower()
        html += f'<tr><td>{r.case_id}</td><td>{r.module}</td><td>{r.name}</td><td>{r.method}</td><td>{r.url}</td><td>{r.expected_code}</td><td>{r.actual_code}</td><td>{r.duration:.0f}ms</td><td><span class="badge {badge_class}">{r.status}</span></td></tr>\n'
    html += '</tbody></table></div></body></html>'

    filepath = os.path.join(REPORT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return filepath


def generate_json_report(tester, filename):
    """生成JSON测试报告"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    stats = tester.get_stats()
    duration = (datetime.now() - tester.start_time).total_seconds()
    report = {
        "summary": {
            "start_time": tester.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": f"{duration:.2f}s",
            "total": stats["total"], "passed": stats["passed"],
            "failed": stats["failed"], "error": stats["error"],
            "pass_rate": f"{(stats['passed']/stats['total']*100):.1f}%" if stats["total"] > 0 else "0%"
        },
        "results": [{"id": r.case_id, "module": r.module, "name": r.name,
            "method": r.method, "url": r.url, "expected": r.expected_code,
            "actual": r.actual_code, "status": r.status, "duration": f"{r.duration:.0f}ms"
        } for r in tester.results]
    }
    filepath = os.path.join(REPORT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return filepath


def run_all_tests():
    """执行所有测试用例"""
    t = APITester()
    print("=" * 60)
    print("  API Test Suite - Full Coverage")
    print("=" * 60)

    # ========== 1. 认证模块测试 (F024/F025) ==========
    print("\n[1. Auth Module - F024/F025]")

    # 1.1 未登录访问受保护接口 (权限控制)
    t.run_test("Unauthorized access", "Auth", "GET", "/api/students", expected=401)
    t.run_test("Unauthorized-courses", "Auth", "GET", "/api/courses", expected=401)
    t.run_test("Unauthorized-enrollments", "Auth", "GET", "/api/enrollments", expected=401)

    # 1.2 登录异常场景
    t.run_test("Login-wrong password", "Auth", "POST", "/api/login",
        {"username": "admin", "password": "wrongpwd"}, expected=401)
    t.run_test("Login-empty username", "Auth", "POST", "/api/login",
        {"username": "", "password": "123"}, expected=400)
    t.run_test("Login-empty password", "Auth", "POST", "/api/login",
        {"username": "admin", "password": ""}, expected=400)
    t.run_test("Login-nonexistent user", "Auth", "POST", "/api/login",
        {"username": "notexist", "password": "123"}, expected=401)

    # 1.3 正常登录
    ok, _ = t.login()
    if not ok:
        print("  [X] Login failed, abort")
        return t
    print("  [OK] Login success")

    # 1.4 登出测试
    t.run_test("Logout", "Auth", "POST", "/api/logout")

    # 1.5 登出后访问受保护接口
    t.run_test("Access after logout", "Auth", "GET", "/api/students", expected=401)

    # 重新登录继续测试
    t.login()

    # ========== 2. Student Module (F001-F004) ==========
    print("\n[2. Student Module - F001/F002/F003/F004]")

    # 2.1 查询测试
    t.run_test("Get student list", "Student", "GET", "/api/students")
    t.run_test("Paginate students", "Student", "GET", "/api/students", {"page": 1, "per_page": 5})
    t.run_test("Paginate page2", "Student", "GET", "/api/students", {"page": 2, "per_page": 5})
    t.run_test("Filter by status-在读", "Student", "GET", "/api/students", {"status": "在读"})
    t.run_test("Filter by status-休学", "Student", "GET", "/api/students", {"status": "休学"})
    t.run_test("Search by keyword", "Student", "GET", "/api/students", {"keyword": "张"})
    t.run_test("Combined filter", "Student", "GET", "/api/students", {"status": "在读", "keyword": "王"})
    
    # 2.2 创建测试 (F001)
    res = t.run_test("Create student-normal", "Student", "POST", "/api/students",
        {"name": "TestStudent", "gender": "男", "age": 25, "phone": "13800001111"})
    sid = res.get("data", {}).get("id")

    t.run_test("Create student-empty name", "Student", "POST", "/api/students",
        {"name": "", "gender": "男"}, expected=400)
    t.run_test("Create student-minimal", "Student", "POST", "/api/students",
        {"name": "MinimalStudent"})
    t.run_test("Create student-female", "Student", "POST", "/api/students",
        {"name": "TestFemale", "gender": "女", "age": 22})

    # 2.3 边界值测试
    t.run_test("Create student-age boundary 0", "Student", "POST", "/api/students",
        {"name": "AgeBoundary0", "age": 0})
    t.run_test("Create student-age boundary 100", "Student", "POST", "/api/students",
        {"name": "AgeBoundary100", "age": 100})
    
    # 2.4 更新测试 (F003)
    if sid:
        t.run_test("Get student detail", "Student", "GET", f"/api/students/{sid}")
        t.run_test("Update student info", "Student", "PUT", f"/api/students/{sid}",
            {"name": "TestStudentUpdated", "age": 26})
        t.run_test("Update student phone", "Student", "PUT", f"/api/students/{sid}",
            {"phone": "13900002222"})

    # 2.5 状态管理测试 (F004)
    if sid:
        t.run_test("Status: 在读->休学", "Student", "PATCH", f"/api/students/{sid}/status",
            {"status": "休学"})
        t.run_test("Status: 休学->在读", "Student", "PATCH", f"/api/students/{sid}/status",
            {"status": "在读"})

    # 2.6 异常测试
    t.run_test("Get nonexistent student", "Student", "GET", "/api/students/99999", expected=404)
    t.run_test("Update nonexistent student", "Student", "PUT", "/api/students/99999",
        {"name": "test"}, expected=404)

    # ========== 3. Course Module (F007-F009) ==========
    print("\n[3. Course Module - F007/F008/F009]")

    # 3.1 查询测试
    t.run_test("Get course list", "Course", "GET", "/api/courses")
    t.run_test("Paginate courses", "Course", "GET", "/api/courses", {"page": 1, "per_page": 5})
    t.run_test("Filter by category", "Course", "GET", "/api/courses", {"category": "编程"})
    
    # 3.2 创建测试 (F007)
    res = t.run_test("Create course-normal", "Course", "POST", "/api/courses",
        {"name": "TestCourse", "category": "测试", "hours": 32, "price": 1999, "teacher": "TestTeacher"})
    cid = res.get("data", {}).get("id")

    t.run_test("Create course-empty name", "Course", "POST", "/api/courses",
        {"name": "", "category": "test"}, expected=400)
    t.run_test("Create course-minimal", "Course", "POST", "/api/courses",
        {"name": "MinimalCourse"})

    # 3.3 更新测试
    if cid:
        t.run_test("Get course detail", "Course", "GET", f"/api/courses/{cid}")
        t.run_test("Update course price", "Course", "PUT", f"/api/courses/{cid}",
            {"price": 2999})
        t.run_test("Update course teacher", "Course", "PUT", f"/api/courses/{cid}",
            {"teacher": "NewTeacher"})

    # 3.4 异常测试
    t.run_test("Get nonexistent course", "Course", "GET", "/api/courses/99999", expected=404)

    # ========== 4. Enrollment Module (F010-F012) ==========
    print("\n[4. Enrollment Module - F010/F011/F012]")

    # 4.1 查询测试
    t.run_test("Get enrollment list", "Enrollment", "GET", "/api/enrollments")
    t.run_test("Paginate enrollments", "Enrollment", "GET", "/api/enrollments", {"page": 1, "per_page": 5})
    # 4.1.1 筛选测试（新增功能）
    t.run_test("Filter by student", "Enrollment", "GET", "/api/enrollments", {"student_id": 1})
    t.run_test("Filter by course", "Enrollment", "GET", "/api/enrollments", {"course_id": 1})
    t.run_test("Filter by status-arrears", "Enrollment", "GET", "/api/enrollments", {"status": "arrears"})
    t.run_test("Filter by status-paid", "Enrollment", "GET", "/api/enrollments", {"status": "paid"})
    
    eid = None
    if sid and cid:
        # 4.2 报名测试 (F010)
        res = t.run_test("Create enrollment", "Enrollment", "POST", "/api/enrollments",
            {"student_id": sid, "course_id": cid})
        eid = res.get("data", {}).get("id")

        # 4.3 重复报名检测
        t.run_test("Duplicate enrollment", "Enrollment", "POST", "/api/enrollments",
            {"student_id": sid, "course_id": cid}, expected=409)
        
        # 4.4 缴费测试 (F011)
        if eid:
            t.run_test("Payment-normal", "Enrollment", "POST", "/api/payments",
                {"enrollment_id": eid, "amount": 500, "method": "微信"})
            t.run_test("Payment-cash", "Enrollment", "POST", "/api/payments",
                {"enrollment_id": eid, "amount": 200, "method": "现金"})
            t.run_test("Payment-zero amount", "Enrollment", "POST", "/api/payments",
                {"enrollment_id": eid, "amount": 0, "method": "微信"}, expected=400)
            t.run_test("Payment-negative", "Enrollment", "POST", "/api/payments",
                {"enrollment_id": eid, "amount": -100, "method": "微信"}, expected=400)

    # ========== 5. Attendance Module (F014-F017) ==========
    print("\n[5. Attendance Module - F014/F015/F016/F017]")

    # 5.1 查询测试
    t.run_test("Get attendance list", "Attendance", "GET", "/api/attendances")
    t.run_test("Paginate attendance", "Attendance", "GET", "/api/attendances", {"page": 1, "per_page": 5})
    # 5.2 筛选测试
    t.run_test("Filter by date range", "Attendance", "GET", "/api/attendances",
        {"start_date": "2026-01-01", "end_date": "2026-02-28"})
    t.run_test("Filter by status-出勤", "Attendance", "GET", "/api/attendances", {"status": "出勤"})
    t.run_test("Filter by status-缺勤", "Attendance", "GET", "/api/attendances", {"status": "缺勤"})
    t.run_test("Filter by status-请假", "Attendance", "GET", "/api/attendances", {"status": "请假"})
    t.run_test("Filter by course", "Attendance", "GET", "/api/attendances", {"course_id": 1})
    t.run_test("Filter by student", "Attendance", "GET", "/api/attendances", {"student_id": 1})

    # 5.3 学员已报名课程API测试
    t.run_test("Get enrolled courses", "Attendance", "GET", "/api/students/1/enrolled-courses")
    t.run_test("Get enrolled courses-nonexistent", "Attendance", "GET", "/api/students/99999/enrolled-courses")
    
    # 5.4 考勤记录测试 (F014)
    if sid and cid:
        today = date.today().strftime("%Y-%m-%d")
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        t.run_test("Create attendance-出勤", "Attendance", "POST", "/api/attendances",
            {"student_id": sid, "course_id": cid, "date": today, "status": "出勤"})
        t.run_test("Create attendance-缺勤", "Attendance", "POST", "/api/attendances",
            {"student_id": sid, "course_id": cid, "date": yesterday, "status": "缺勤"})

    # 5.5 未报名学员录入考勤拒绝测试
    t.run_test("Attendance-not enrolled", "Attendance", "POST", "/api/attendances",
        {"student_id": 1, "course_id": 99999, "date": date.today().strftime("%Y-%m-%d"), "status": "出勤"}, expected=400)

    # ========== 6. Statistics Module (F018-F020) ==========
    print("\n[6. Statistics Module - F018/F019/F020]")

    t.run_test("Dashboard stats", "Statistics", "GET", "/api/statistics/dashboard")
    t.run_test("Chart data", "Statistics", "GET", "/api/statistics/charts")

    # ========== 7. 删除约束测试 ==========
    print("\n[7. Delete Constraint Tests]")

    # 有报名记录的学员不可删除（返回409冲突）
    t.run_test("Delete student with enrollment", "Constraint", "DELETE", "/api/students/1", expected=409)
    # 有报名记录的课程不可删除（返回409冲突）
    t.run_test("Delete course with enrollment", "Constraint", "DELETE", "/api/courses/1", expected=409)

    # ========== 7. Cleanup ==========
    print("\n[7. Cleanup]")

    # 按依赖顺序删除：考勤 -> 报名 -> 学员/课程
    # 注意：考勤记录没有删除API，跳过
    if eid:
        t.run_test("Delete test enrollment", "Cleanup", "DELETE", f"/api/enrollments/{eid}")

    # 删除 MinimalStudent（无关联数据）
    res = t.session.get(f"{BASE_URL}/api/students", params={"keyword": "MinimalStudent"})
    if res.status_code == 200:
        data = res.json().get("data", {}).get("list", [])
        for s in data:
            if s.get("name") == "MinimalStudent":
                t.run_test("Delete MinimalStudent", "Cleanup", "DELETE", f"/api/students/{s['id']}")

    # ========== Summary ==========
    print("\n" + "=" * 60)
    stats = t.get_stats()
    print(f"  Total: {stats['total']} | Pass: {stats['passed']} | Fail: {stats['failed']} | Error: {stats['error']}")
    pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"  Pass Rate: {pass_rate:.1f}%")
    print("=" * 60)

    return t


def main():
    """主函数"""
    print("\nStarting API Test Suite...")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    tester = run_all_tests()

    # 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = generate_html_report(tester, f"report_{timestamp}.html")
    json_file = generate_json_report(tester, f"report_{timestamp}.json")

    print(f"\nReports generated:")
    print(f"  HTML: {html_file}")
    print(f"  JSON: {json_file}")

    return tester.get_stats()


if __name__ == "__main__":
    main()
