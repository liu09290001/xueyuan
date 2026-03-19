#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Student, Course, Enrollment, Payment, Attendance

# 真实姓名库
SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '林']
NAMES = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '涛', '明', '超', '秀英', '桂英']

# 真实课程库
COURSES_DATA = [
    ('Python基础', '编程', 48, 2980),
    ('Java开发', '编程', 64, 3980),
    ('Web前端开发', '编程', 56, 3580),
    ('UI设计基础', '设计', 40, 2680),
    ('平面设计', '设计', 48, 2880),
    ('新媒体运营', '运营', 32, 2380),
    ('数据分析', '编程', 40, 3280),
    ('产品经理', '管理', 36, 3680)
]

def generate_students(count=50):
    students = []
    for i in range(count):
        student = Student(
            name=random.choice(SURNAMES) + random.choice(NAMES),
            gender=random.choice(['男', '女']),
            age=random.randint(20, 40),
            phone=f"138{random.randint(10000000, 99999999)}",
            status='在读'
        )
        students.append(student)
    db.session.add_all(students)
    db.session.commit()
    print(f"生成{count}个学员")
    return students

def generate_courses(count=20):
    courses = []
    for i in range(count):
        base = random.choice(COURSES_DATA)
        course = Course(
            name=base[0] if i < 8 else f"{base[0]}{i-7}期",
            category=base[1],
            hours=base[2],
            price=base[3]
        )
        courses.append(course)
    db.session.add_all(courses)
    db.session.commit()
    print(f"生成{count}个课程")
    return courses

def generate_enrollments(students, courses, count=100):
    enrollments = []
    for _ in range(count):
        course = random.choice(courses)
        enrollment = Enrollment(
            student_id=random.choice(students).id,
            course_id=course.id,
            amount=course.price,
            paid=0,
            status='已报名'
        )
        enrollments.append(enrollment)
    db.session.add_all(enrollments)
    db.session.commit()
    print(f"生成{count}条报名")
    return enrollments

def generate_payments(enrollments):
    payments = []
    for enrollment in enrollments:
        paid = random.choice([enrollment.amount, enrollment.amount//2])
        payment = Payment(enrollment_id=enrollment.id, amount=paid)
        payments.append(payment)
        enrollment.paid = paid
    db.session.add_all(payments)
    db.session.commit()
    print(f"生成{len(payments)}条缴费")

def generate_attendances(enrollments, count=200):
    attendances = []
    for _ in range(count):
        enrollment = random.choice(enrollments)
        attendance = Attendance(
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            date=datetime.now() - timedelta(days=random.randint(1, 90)),
            status=random.choice(['出勤', '缺勤', '请假'])
        )
        attendances.append(attendance)
    db.session.add_all(attendances)
    db.session.commit()
    print(f"生成{count}条考勤")

def main():
    app = create_app()
    with app.app_context():
        print("开始生成测试数据...")
        students = generate_students(50)
        courses = generate_courses(20)
        enrollments = generate_enrollments(students, courses, 100)
        generate_payments(enrollments)
        generate_attendances(enrollments, 200)
        print("完成！")

if __name__ == "__main__":
    main()
