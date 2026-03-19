# -*- coding: utf-8 -*-
"""批量生成测试数据"""
import requests
import time

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

students = [
    {"name": "张伟", "gender": "男", "age": 22, "phone": "13800001001"},
    {"name": "王芳", "gender": "女", "age": 20, "phone": "13800001002"},
    {"name": "李明", "gender": "男", "age": 25, "phone": "13800001003"},
    {"name": "刘洋", "gender": "男", "age": 23, "phone": "13800001004"},
    {"name": "陈静", "gender": "女", "age": 21, "phone": "13800001005"},
    {"name": "杨帆", "gender": "男", "age": 24, "phone": "13800001006"},
    {"name": "赵敏", "gender": "女", "age": 19, "phone": "13800001007"},
    {"name": "黄磊", "gender": "男", "age": 26, "phone": "13800001008"},
    {"name": "周婷", "gender": "女", "age": 22, "phone": "13800001009"},
    {"name": "吴强", "gender": "男", "age": 28, "phone": "13800001010"},
    {"name": "徐丽", "gender": "女", "age": 20, "phone": "13800001011"},
    {"name": "孙浩", "gender": "男", "age": 23, "phone": "13800001012"},
    {"name": "马云飞", "gender": "男", "age": 25, "phone": "13800001013"},
    {"name": "朱雪", "gender": "女", "age": 21, "phone": "13800001014"},
    {"name": "胡建国", "gender": "男", "age": 27, "phone": "13800001015"},
]

courses = [
    {"name": "Python编程入门", "category": "编程", "hours": 48, "price": 2999, "teacher": "王老师"},
    {"name": "Java高级开发", "category": "编程", "hours": 64, "price": 4999, "teacher": "李老师"},
    {"name": "Web前端开发", "category": "编程", "hours": 56, "price": 3999, "teacher": "张老师"},
    {"name": "数据分析实战", "category": "数据", "hours": 40, "price": 3599, "teacher": "刘老师"},
    {"name": "人工智能基础", "category": "AI", "hours": 72, "price": 5999, "teacher": "陈老师"},
    {"name": "UI设计精品班", "category": "设计", "hours": 48, "price": 3299, "teacher": "赵老师"},
    {"name": "产品经理实战", "category": "产品", "hours": 36, "price": 2799, "teacher": "孙老师"},
    {"name": "软件测试入门", "category": "测试", "hours": 32, "price": 2499, "teacher": "周老师"},
]

def create_data():
    print("="*40)
    print("开始批量创建测试数据")
    print("="*40)
    
    # 登录
    print("\n登录中...")
    resp = session.post(f"{BASE_URL}/api/login", json={"username": "admin", "password": "admin123"}, timeout=10)
    if resp.status_code != 200:
        print(f"登录失败: {resp.status_code}")
        return
    print("登录成功")
    
    student_ids = []
    course_ids = []
    
    # 创建学员
    print(f"\n--- 创建学员 ({len(students)}条) ---")
    for s in students:
        time.sleep(0.1)
        resp = session.post(f"{BASE_URL}/api/students", json=s, timeout=5)
        if resp.status_code in [200, 201]:
            sid = resp.json().get("data", {}).get("id")
            student_ids.append(sid)
            print(f"[OK] {s['name']}")
        else:
            print(f"[FAIL] {s['name']}: {resp.status_code}")
    
    # 创建课程
    print(f"\n--- 创建课程 ({len(courses)}条) ---")
    for c in courses:
        time.sleep(0.1)
        resp = session.post(f"{BASE_URL}/api/courses", json=c, timeout=5)
        if resp.status_code in [200, 201]:
            cid = resp.json().get("data", {}).get("id")
            course_ids.append(cid)
            print(f"[OK] {c['name']}")
        else:
            print(f"[FAIL] {c['name']}: {resp.status_code}")
    
    # 创建报名
    print(f"\n--- 创建报名记录 (7条) ---")
    enrollments = []
    for i in range(min(7, len(student_ids), len(course_ids))):
        time.sleep(0.1)
        data = {"student_id": student_ids[i], "course_id": course_ids[i % len(course_ids)]}
        resp = session.post(f"{BASE_URL}/api/enrollments", json=data, timeout=5)
        if resp.status_code in [200, 201]:
            eid = resp.json().get("data", {}).get("id")
            enrollments.append(eid)
            print(f"[OK] 学员{student_ids[i]} -> 课程{course_ids[i % len(course_ids)]}")
        else:
            print(f"[FAIL] 学员{student_ids[i]}: {resp.status_code}")
    
    print(f"\n{'='*40}")
    print(f"数据创建完成!")
    print(f"学员: {len(student_ids)}, 课程: {len(course_ids)}, 报名: {len(enrollments)}")
    print(f"总计: {len(student_ids) + len(course_ids) + len(enrollments)}条")
    print("="*40)

if __name__ == "__main__":
    create_data()
