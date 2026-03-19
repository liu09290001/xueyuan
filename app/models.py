# -*- coding: utf-8 -*-
"""
数据库模型定义
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(256), nullable=False, comment='密码哈希')
    role = db.Column(db.String(20), default='user', comment='角色:admin/user')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    """学员模型"""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True, comment='姓名')
    gender = db.Column(db.String(10), comment='性别')
    age = db.Column(db.Integer, comment='年龄')
    phone = db.Column(db.String(20), index=True, comment='联系电话')
    emergency_contact = db.Column(db.String(50), comment='紧急联系人')
    emergency_phone = db.Column(db.String(20), comment='紧急联系电话')
    status = db.Column(db.String(20), default='在读', index=True, comment='状态:在读/休学/结业/退学')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    attendances = db.relationship('Attendance', backref='student', lazy='dynamic')


class Course(db.Model):
    """课程模型"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='课程名称')
    category = db.Column(db.String(50), comment='课程类别')
    hours = db.Column(db.Integer, comment='课时')
    price = db.Column(db.Float, comment='单价')
    validity = db.Column(db.Integer, comment='有效期(月)')
    teacher = db.Column(db.String(50), comment='教师')
    room = db.Column(db.String(50), comment='教室')
    schedule = db.Column(db.String(100), comment='上课时间')
    status = db.Column(db.String(20), default='开课中', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now)

    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')


class Enrollment(db.Model):
    """报名记录模型"""
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    amount = db.Column(db.Float, default=0, comment='应缴金额')
    paid = db.Column(db.Float, default=0, comment='已缴金额')
    status = db.Column(db.String(20), default='已报名', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now)

    payments = db.relationship('Payment', backref='enrollment', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'amount': self.amount,
            'paid': self.paid,
            'status': self.status
        }


class Payment(db.Model):
    """缴费记录模型"""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False, comment='缴费金额')
    method = db.Column(db.String(20), comment='支付方式')
    receiver = db.Column(db.String(50), comment='收款人')
    receipt_no = db.Column(db.String(50), comment='收据编号')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'enrollment_id': self.enrollment_id,
            'amount': self.amount,
            'method': self.method,
            'receiver': self.receiver,
            'receipt_no': self.receipt_no,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Attendance(db.Model):
    """考勤记录模型"""
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, comment='日期')
    status = db.Column(db.String(20), default='出勤', comment='状态:出勤/缺勤/迟到/请假')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关联课程
    course = db.relationship('Course', backref='attendances')
