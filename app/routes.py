# -*- coding: utf-8 -*-
"""
路由注册
"""
import uuid
from flask import Blueprint, render_template, jsonify, request, make_response
from sqlalchemy import func
from app.models import db, User, Student, Course, Enrollment, Payment, Attendance
from app.utils import logger, login_required, rate_limit, generate_token, Validator
from datetime import datetime, date

# 创建蓝图
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')


def register_blueprints(app):
    """注册所有蓝图"""
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)


# ========== 页面路由 ==========
@main_bp.route('/login')
def login_page():
    """登录页"""
    return render_template('login.html')


@main_bp.route('/')
def index():
    """首页仪表盘"""
    return render_template('index.html')


@main_bp.route('/students')
def students_page():
    """学员管理页"""
    return render_template('students.html')


@main_bp.route('/courses')
def courses_page():
    """课程管理页"""
    return render_template('courses.html')


@main_bp.route('/enrollments')
def enrollments_page():
    """报名缴费页"""
    return render_template('enrollments.html')


@main_bp.route('/attendance')
def attendance_page():
    """考勤管理页"""
    return render_template('attendance.html')


@main_bp.route('/statistics')
def statistics_page():
    """数据统计页"""
    return render_template('statistics.html')


# ========== 认证API ==========
@api_bp.route('/login', methods=['POST'])
@rate_limit(limit=10, window=60)
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'code': 40001, 'msg': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        logger.warning(f'登录失败: {username}')
        return jsonify({'code': 40101, 'msg': '用户名或密码错误'}), 401

    token = generate_token(user.id, user.username, user.role)
    logger.info(f'用户登录: {username}')

    resp = make_response(jsonify({'code': 0, 'data': {'token': token, 'username': username}}))
    resp.set_cookie('token', token, max_age=86400, httponly=True, samesite='Lax', path='/')
    return resp


@api_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    resp = make_response(jsonify({'code': 0, 'msg': '已登出'}))
    resp.delete_cookie('token')
    return resp


# ========== 学员API ==========
@api_bp.route('/students', methods=['GET'])
@login_required
def get_students():
    """获取学员列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', '')
    keyword = request.args.get('keyword', '')

    query = Student.query
    if status:
        query = query.filter(Student.status == status)
    if keyword:
        query = query.filter(Student.name.contains(keyword))

    pagination = query.order_by(Student.id.asc()).paginate(page=page, per_page=per_page)
    students = [{
        'id': s.id, 'name': s.name, 'gender': s.gender,
        'age': s.age, 'phone': s.phone, 'status': s.status,
        'created_at': s.created_at.strftime('%Y-%m-%d')
    } for s in pagination.items]

    return jsonify({'code': 0, 'data': {'list': students, 'total': pagination.total}})


@api_bp.route('/students', methods=['POST'])
@login_required
@rate_limit(limit=30, window=60)
def create_student():
    """新增学员"""
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'code': 40001, 'msg': '姓名不能为空'}), 400

    # age类型转换
    age = data.get('age')
    if age:
        try:
            age = int(age)
        except (ValueError, TypeError):
            age = None

    try:
        student = Student(
            name=data['name'],
            gender=data.get('gender'),
            age=age,
            phone=data.get('phone'),
            emergency_contact=data.get('emergency_contact'),
            emergency_phone=data.get('emergency_phone')
        )
        db.session.add(student)
        db.session.commit()
        return jsonify({'code': 0, 'msg': 'success', 'data': {'id': student.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 50001, 'msg': '创建失败'}), 500


@api_bp.route('/students/<int:id>', methods=['GET'])
@login_required
def get_student(id):
    """获取学员详情"""
    student = Student.query.get_or_404(id)
    return jsonify({'code': 0, 'data': {
        'id': student.id, 'name': student.name, 'gender': student.gender,
        'age': student.age, 'phone': student.phone, 'status': student.status,
        'emergency_contact': student.emergency_contact,
        'emergency_phone': student.emergency_phone
    }})


@api_bp.route('/students/<int:id>', methods=['PUT'])
@login_required
def update_student(id):
    """更新学员信息"""
    student = Student.query.get_or_404(id)
    data = request.get_json()
    for key in ['name', 'gender', 'age', 'phone', 'emergency_contact', 'emergency_phone']:
        if key in data:
            setattr(student, key, data[key])
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@api_bp.route('/students/<int:id>/status', methods=['PATCH'])
@login_required
def update_student_status(id):
    """更新学员状态"""
    student = Student.query.get_or_404(id)
    data = request.get_json()
    student.status = data.get('status', student.status)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@api_bp.route('/students/<int:id>', methods=['DELETE'])
@login_required
def delete_student(id):
    """删除学员"""
    student = Student.query.get_or_404(id)
    # 检查是否有关联的报名记录
    if Enrollment.query.filter_by(student_id=id).first():
        return jsonify({'code': 40901, 'msg': '该学员有报名记录，无法删除'}), 409
    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'code': 0, 'msg': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 50001, 'msg': '删除失败'}), 500


# ========== 课程API ==========
@api_bp.route('/courses', methods=['GET'])
@login_required
def get_courses():
    """获取课程列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')

    query = Course.query
    if category:
        query = query.filter(Course.category == category)
    if keyword:
        query = query.filter(Course.name.contains(keyword))

    pagination = query.order_by(Course.id.asc()).paginate(page=page, per_page=per_page)
    courses = [{
        'id': c.id, 'name': c.name, 'category': c.category,
        'hours': c.hours, 'price': c.price, 'teacher': c.teacher,
        'room': c.room, 'status': c.status
    } for c in pagination.items]
    return jsonify({'code': 0, 'data': {'list': courses, 'total': pagination.total}})


@api_bp.route('/courses', methods=['POST'])
@login_required
@rate_limit(limit=30, window=60)
def create_course():
    """新增课程"""
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'code': 40001, 'msg': '课程名称不能为空'}), 400
    course = Course(
        name=data['name'], category=data.get('category'),
        hours=data.get('hours'), price=data.get('price'),
        validity=data.get('validity'), teacher=data.get('teacher'),
        room=data.get('room'), schedule=data.get('schedule')
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({'code': 0, 'data': {'id': course.id}})


@api_bp.route('/courses/<int:id>', methods=['GET'])
@login_required
def get_course(id):
    """获取课程详情"""
    course = Course.query.get_or_404(id)
    return jsonify({'code': 0, 'data': {
        'id': course.id, 'name': course.name, 'category': course.category,
        'hours': course.hours, 'price': course.price, 'teacher': course.teacher
    }})


@api_bp.route('/courses/<int:id>', methods=['PUT'])
@login_required
def update_course(id):
    """更新课程"""
    course = Course.query.get_or_404(id)
    data = request.get_json()
    for key in ['name', 'category', 'hours', 'price', 'teacher', 'room', 'schedule']:
        if key in data:
            setattr(course, key, data[key])
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@api_bp.route('/courses/<int:id>', methods=['DELETE'])
@login_required
def delete_course(id):
    """删除课程"""
    course = Course.query.get_or_404(id)
    # 检查是否有关联的报名记录
    if Enrollment.query.filter_by(course_id=id).first():
        return jsonify({'code': 40901, 'msg': '该课程有报名记录，无法删除'}), 409
    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({'code': 0, 'msg': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 50001, 'msg': '删除失败'}), 500


# ========== 报名缴费API ==========
@api_bp.route('/enrollments', methods=['GET'])
@login_required
def get_enrollments():
    """获取报名列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    status = request.args.get('status', '')

    query = Enrollment.query
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
    if course_id:
        query = query.filter(Enrollment.course_id == course_id)
    # 状态筛选：在数据库层面过滤
    if status == 'arrears':
        query = query.filter(Enrollment.amount > Enrollment.paid)
    elif status == 'paid':
        query = query.filter(Enrollment.amount <= Enrollment.paid)

    pagination = query.order_by(Enrollment.id.asc()).paginate(page=page, per_page=per_page)
    result = [{
        'id': e.id, 'student_id': e.student_id,
        'student_name': e.student.name,
        'course_id': e.course_id, 'course_name': e.course.name,
        'amount': e.amount, 'paid': e.paid,
        'arrears': e.amount - e.paid, 'status': e.status
    } for e in pagination.items]
    return jsonify({'code': 0, 'data': {'list': result, 'total': pagination.total}})


@api_bp.route('/enrollments', methods=['POST'])
@login_required
@rate_limit(limit=30, window=60)
def create_enrollment():
    """新增报名"""
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    # 检查是否重复报名
    exists = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if exists:
        return jsonify({'code': 40901, 'msg': '该学员已报名此课程'}), 409

    course = Course.query.get(course_id)
    enrollment = Enrollment(
        student_id=student_id, course_id=course_id,
        amount=course.price if course else 0
    )
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({'code': 0, 'data': {'id': enrollment.id}})


@api_bp.route('/enrollments/<int:id>', methods=['GET'])
@login_required
def get_enrollment(id):
    """查询报名详情"""
    enrollment = Enrollment.query.get_or_404(id)
    return jsonify({'code': 0, 'data': enrollment.to_dict()})

@api_bp.route('/enrollments/<int:id>', methods=['DELETE'])
@login_required
def delete_enrollment(id):
    """删除报名记录"""
    enrollment = Enrollment.query.get_or_404(id)
    # 先删除关联的缴费记录
    Payment.query.filter_by(enrollment_id=id).delete()
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})




@api_bp.route('/payments', methods=['GET'])
@login_required
def get_payments():
    """查询缴费记录"""
    enrollment_id = request.args.get('enrollment_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Payment.query
    if enrollment_id:
        query = query.filter_by(enrollment_id=enrollment_id)

    pagination = query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 0,
        'data': {
            'items': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })

@api_bp.route('/payments', methods=['POST'])
@login_required
@rate_limit(limit=30, window=60)
def create_payment():
    """新增缴费记录"""
    data = request.get_json()
    enrollment_id = data.get('enrollment_id')
    # 确保 amount 转换为浮点数，处理 None 和字符串情况
    try:
        amount = float(data.get('amount') or 0)
    except (TypeError, ValueError):
        return jsonify({'code': 40001, 'msg': '缴费金额格式错误'}), 400

    if amount <= 0:
        return jsonify({'code': 40001, 'msg': '缴费金额必须大于0'}), 400

    enrollment = Enrollment.query.get_or_404(enrollment_id)

    # 校验缴费金额不能超过欠费
    arrears = enrollment.amount - enrollment.paid
    if amount > arrears:
        return jsonify({'code': 40002, 'msg': f'缴费金额不能超过欠费金额{arrears}元'}), 400

    try:
        receipt_no = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
        payment = Payment(
            enrollment_id=enrollment_id, amount=amount,
            method=data.get('method'), receiver=data.get('receiver'),
            receipt_no=receipt_no
        )
        enrollment.paid += amount
        db.session.add(payment)
        db.session.commit()
        return jsonify({'code': 0, 'data': {'id': payment.id, 'receipt_no': payment.receipt_no}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 50001, 'msg': '缴费失败'}), 500


# ========== 考勤API ==========
@api_bp.route('/attendances', methods=['GET'])
@login_required
def get_attendances():
    """获取考勤记录"""
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Attendance.query
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if course_id:
        query = query.filter(Attendance.course_id == course_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    if status:
        query = query.filter(Attendance.status == status)

    pagination = query.order_by(Attendance.date.desc()).paginate(page=page, per_page=per_page)
    records = [{
        'id': a.id, 'student_id': a.student_id,
        'student_name': a.student.name,
        'course_id': a.course_id,
        'course_name': a.course.name if a.course else '-',
        'date': str(a.date), 'status': a.status
    } for a in pagination.items]
    return jsonify({'code': 0, 'data': {'list': records, 'total': pagination.total}})


@api_bp.route('/students/<int:id>/enrolled-courses', methods=['GET'])
@login_required
def get_student_enrolled_courses(id):
    """获取学员已报名的课程列表"""
    enrollments = Enrollment.query.filter_by(student_id=id).all()
    courses = [{'id': e.course.id, 'name': e.course.name} for e in enrollments if e.course]
    return jsonify({'code': 0, 'data': courses})


@api_bp.route('/attendances', methods=['POST'])
@login_required
def create_attendance():
    """记录考勤 - 需验证学员已报名该课程"""
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    # 校验学员是否已报名该课程
    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if not enrollment:
        return jsonify({'code': 40001, 'msg': '该学员未报名此课程，无法录入考勤'}), 400

    attendance = Attendance(
        student_id=student_id,
        course_id=course_id,
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
        status=data.get('status', '出勤')
    )
    db.session.add(attendance)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


# ========== 统计API ==========
@api_bp.route('/statistics/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    """仪表盘数据"""
    student_count = Student.query.count()
    course_count = Course.query.count()
    enrollment_count = Enrollment.query.count()

    # 本月收入
    today = date.today()
    month_start = today.replace(day=1)
    month_income = db.session.query(func.sum(Payment.amount)).filter(
        Payment.created_at >= month_start
    ).scalar() or 0

    return jsonify({'code': 0, 'data': {
        'student_count': student_count,
        'course_count': course_count,
        'enrollment_count': enrollment_count,
        'month_income': month_income
    }})


@api_bp.route('/statistics/charts', methods=['GET'])
@login_required
def get_charts_data():
    """图表统计数据"""
    # 学员状态分布
    status_data = db.session.query(Student.status, func.count(Student.id)).group_by(Student.status).all()
    student_status = {s: c for s, c in status_data}

    # 课程报名统计
    course_data = db.session.query(
        Course.name, func.count(Enrollment.id)
    ).outerjoin(Enrollment, Course.id == Enrollment.course_id).group_by(Course.id, Course.name).all()
    course_enrollment = {name: count for name, count in course_data}

    # 课程出勤率统计
    attendance_rate = {}
    courses = Course.query.all()
    for course in courses:
        total = Attendance.query.filter_by(course_id=course.id).count()
        if total > 0:
            present = Attendance.query.filter_by(course_id=course.id, status='出勤').count()
            attendance_rate[course.name] = round(present / total * 100, 1)

    return jsonify({'code': 0, 'data': {
        'student_status': student_status,
        'course_enrollment': course_enrollment,
        'attendance_rate': attendance_rate
    }})
