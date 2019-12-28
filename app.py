import json
import operator
from itertools import groupby

from flask import Flask, request
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from grading.configuration import SQLALCHEMY_DATABASE_URI
from grading.redis_client import set_lock, release_lock
from grading.validators import validate_student, auth, validate_email, validate_course, validate_students, \
    validate_grade, validate_grade_range

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/student', methods = ['POST'])
@auth.login_required
def add_student():
    from grading.models import add_student_model
    student_data = request.get_json()
    first_name = student_data.get('first_name')
    second_name = student_data.get('second_name')
    email = student_data.get('email')
    validate_message = validate_student(first_name, second_name, email)
    if validate_message:
        return validate_message, status.HTTP_400_BAD_REQUEST

    try:
        result = add_student_model(student_data)
    except IntegrityError:
        return 'student email  exists', status.HTTP_409_CONFLICT
    return json.dumps(result), status.HTTP_201_CREATED


@app.route('/student/<int:id>', methods = ['PUT'])
@auth.login_required
def update_student(id):
    from grading.models import update_student_model
    student_data = request.get_json()
    email = student_data.get('email')
    if email:
        message = validate_email(email)
        if message:
            return message, status.HTTP_400_BAD_REQUEST
    try:
        set_lock('student'+str(id))
        if not update_student_model(id, student_data):
            return 'student not found', status.HTTP_404_NOT_FOUND
    finally:
        release_lock('student'+str(id))
    result = {'id': id}
    return json.dumps(result), status.HTTP_200_OK


@app.route('/student/<int:id>', methods = ['DELETE'])
@auth.login_required
def delete_student(id):
    from grading.models import delete_student_model

    try:
        set_lock('student'+str(id))
        if not delete_student_model(id):
            return 'student not found', status.HTTP_404_NOT_FOUND
    finally:
        release_lock('student'+str(id))
    return '', status.HTTP_204_NO_CONTENT


@app.route('/student/<int:id>', methods = ['GET'])
@auth.login_required
def get_student(id):
    from grading.models import get_student_model

    result = get_student_model(id)
    if result:
        return json.dumps(result), status.HTTP_200_OK
    else:
        return 'student not found', status.HTTP_404_NOT_FOUND


@app.route('/course', methods = ['POST'])
@auth.login_required
def add_course():
    from grading.models import add_course_model
    course_data = request.get_json()
    name = course_data.get('name')
    students = course_data.get('students')
    validate_message = validate_course(name, students)
    if validate_message:
        return validate_message, status.HTTP_400_BAD_REQUEST
    try:
        result = add_course_model(course_data)
    except IntegrityError:
        return 'course exists', status.HTTP_409_CONFLICT
    return json.dumps(result), status.HTTP_201_CREATED


@app.route('/course/<int:id>', methods = ['PUT'])
@auth.login_required
def update_course(id):
    from grading.models import update_course_model
    course_data = request.get_json()
    students = course_data.get('students')
    if students:
        message = validate_students(students)
        if message:
            return message, status.HTTP_400_BAD_REQUEST
    try:
        set_lock('course'+str(id))
        if not update_course_model(id, course_data):
            return 'course not found', status.HTTP_404_NOT_FOUND
    finally:
        release_lock('course'+str(id))
    result = {'id': id}
    return json.dumps(result), status.HTTP_200_OK


@app.route('/course/<int:id>', methods = ['DELETE'])
@auth.login_required
def delete_course(id):
    from grading.models import delete_course_model

    try:
        set_lock('course'+str(id))
        if not delete_course_model(id):
            return 'course not found', status.HTTP_404_NOT_FOUND
    finally:
        release_lock('course'+str(id))
    return '', status.HTTP_204_NO_CONTENT


@app.route('/course/<int:id>', methods = ['GET'])
@auth.login_required
def get_course(id):
    from grading.models import get_course_model

    result = get_course_model(id)
    if result:
        return json.dumps(result), status.HTTP_200_OK
    else:
        return 'course not found', status.HTTP_404_NOT_FOUND



@app.route('/grade', methods = ['POST'])
@auth.login_required
def add_grade():
    from grading.models import add_grade_model
    grade_data = request.get_json()
    grade = grade_data.get('grade')
    student = grade_data.get('student')
    course = grade_data.get('course')
    validate_message = validate_grade(grade, student, course)
    if validate_message:
        return validate_message, status.HTTP_400_BAD_REQUEST
    try:
        add_grade_model(grade_data)
    except IntegrityError:
        return 'bad parameters', status.HTTP_400_BAD_REQUEST
    return '', status.HTTP_201_CREATED


@app.route('/grade', methods = ['PUT'])
@auth.login_required
def update_grade():
    from grading.models import update_grade_model
    grade_data = request.get_json()
    grade = grade_data.get('grade')
    student = grade_data.get('student')
    course = grade_data.get('course')
    validate_message = validate_grade(grade, student, course)
    if validate_message:
        return validate_message, status.HTTP_400_BAD_REQUEST
    try:
        set_lock('grade'+str(student)+str(course))
        if not update_grade_model(student, course, {'grade': grade}):
            return 'grade not found', status.HTTP_404_NOT_FOUND
    finally:
        release_lock('grade'+str(student)+str(course))
    return '', status.HTTP_200_OK


@app.route('/grade/<int:student>/<int:course>', methods = ['DELETE'])
@auth.login_required
def delete_grade(student, course):
    from grading.models import delete_grade_model

    try:
        set_lock('grade'+str(student)+str(course))
        if not delete_grade_model(student, course):
            return 'grade not found', status.HTTP_404_NOT_FOUND
    finally:
        release_lock('grade'+str(student)+str(course))
    return '', status.HTTP_204_NO_CONTENT


@app.route('/grade/<int:student>/<int:course>', methods = ['GET'])
@auth.login_required
def get_grade(student, course):
    from grading.models import get_grade_model

    result = get_grade_model(student, course)
    if result:
        return json.dumps(result), status.HTTP_200_OK
    else:
        return 'grade not found', status.HTTP_404_NOT_FOUND


@app.route('/grade', methods = ['GET'])
@auth.login_required
def get_grades():
    from grading.models import get_grade_model
    result = get_grade_model()
    if result:
        return json.dumps(result), status.HTTP_200_OK
    else:
        return 'grade not found', status.HTTP_404_NOT_FOUND


@app.route('/best_student', methods = ['GET'])
@auth.login_required
def get_best_student():
    from grading.models import get_grade_model, get_student_model
    grades = get_grade_model()
    if grades:
        average_score = {}
        for student, grade_list in groupby(grades, key=lambda x: x['student']):
            grade_list = list(grade_list)
            average = float(sum(grade['grade'] for grade in grade_list)) / len(grade_list)
            average_score[student] = average
        best_student = max(average_score.items(), key=operator.itemgetter(1))[0]
        result = get_student_model(best_student)
        return result, status.HTTP_200_OK
    else:
        return 'grades not found', status.HTTP_404_NOT_FOUND


@app.route('/easy_course', methods = ['GET'])
@auth.login_required
def get_easy_course():
    from grading.models import get_grade_model, get_course_model
    grades = get_grade_model()
    if grades:
        average_score = {}
        for course, grade_list in groupby(grades, key=lambda x: x['course']):
            grade_list = list(grade_list)
            average = float(sum(grade['grade'] for grade in grade_list)) / len(grade_list)
            average_score[course] = average
        easy_course = min(average_score.items(), key=operator.itemgetter(1))[0]
        result = get_course_model(easy_course)
        return result, status.HTTP_200_OK
    else:
        return 'grades not found', status.HTTP_404_NOT_FOUND




if __name__ == "__main__":
    with app.app_context():
        from grading.models import create_tables

        create_tables()
    app.run(debug=True)

