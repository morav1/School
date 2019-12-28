from app import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    second_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    grades = db.relationship('Grade', backref='student', lazy=True)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    students = db.Column(db.String(80), unique=False, nullable=False)
    grades = db.relationship('Grade', backref='course', lazy=True)


class Grade(db.Model):
    grade = db.Column(db.Integer, unique=False, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    __table_args__ = (db.PrimaryKeyConstraint('student_id', 'course_id'),)


def add_student_model(student_data):
    object = Student(first_name=student_data['first_name'],
                     second_name=student_data['second_name'],
                     email=student_data['email'])
    return add_model(object)


def add_grade_model(grade_data):
    object = Grade(grade=grade_data['grade'],
                   student_id=int(grade_data['student']),
                   course_id=int(grade_data['course']))
    db.session.add(object)
    db.session.commit()
    db.session.refresh(object)


def add_course_model(course_data):
    object = Course(name=course_data['name'],
                    students=course_data['students'])
    return add_model(object)


def add_model(object):
    db.session.add(object)
    db.session.commit()
    db.session.refresh(object)
    return {'id': object.id}


def get_student_model(id):
    student = Student.query.filter_by(id=id)
    if student.first():
        return {
            'id': student[0].id,
            'first_name': student[0].first_name,
            'second_name': student[0].second_name,
            'email': student[0].email
        }


def get_course_model(id):
    course = Course.query.filter_by(id=id)
    if course.first():
        return {
            'id': course[0].id,
            'name': course[0].name,
            'students': course[0].students
        }

def get_grade_model(student=None, course=None):
    def get_grade(grage_model):
        return {
            'grade': grage_model.grade,
            'student': grage_model.student.id,
            'course': grage_model.course.id
        }
    if not student:
        grades = Grade.query.all()
        return [get_grade(grade_model) for grade_model in grades]
    else:
        grade_model = Grade.query.filter_by(student_id=student, course_id=course)
        if grade_model.first():
            return get_grade(grade_model[0])


def delete_student_model(id):
    student = Student.query.filter_by(id=id)
    if student.first():
        student.delete()
        db.session.commit()
        return True
    return False


def delete_grade_model(student, course):
    grade = Grade.query.filter_by(student_id=student, course_id=course)
    if grade.first():
        grade.delete()
        db.session.commit()
        return True
    return False


def delete_course_model(id):
    course = Course.query.filter_by(id=id)
    if course.first():
        course.delete()
        db.session.commit()
        return True
    return False


def update_student_model(id, student_data):
    student = Student.query.filter_by(id=id)
    if student.first():
        student.update(student_data)
        db.session.commit()
        return True
    return False


def update_course_model(id, course_data):
    course = Course.query.filter_by(id=id)
    if course.first():
        course.update(course_data)
        db.session.commit()
        return True
    return False


def update_grade_model(student, course, grade):
    object = Grade.query.filter_by(student_id=student, course_id=course)
    if object.first():
        object.update(grade)
        db.session.commit()
        return True
    return False


def students_count(students_list):
    return len(db.session.query(Student).filter(Student.id.in_(students_list)).all())


def create_tables():
    db.create_all()
    db.session.commit()