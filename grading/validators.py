import json
import re

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from grading.configuration import ALLOWED_CREDENTIALS


email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
auth = HTTPBasicAuth()
credentials = json.loads(ALLOWED_CREDENTIALS)

@auth.verify_password
def verify_password(username, password):
    if username in credentials:
        return check_password_hash(generate_password_hash(credentials.get(username)), password)
    return False


def validate_email(email):
    if not re.search(email_regex,email):
        return 'email not valid'
    return ''

def validate_student(first_name, second_name, email):
    if not first_name:
        message = 'missing first name'
    elif not second_name:
        message = 'missing second name'
    elif not email:
        message = 'missing email'
    else:
        message = validate_email(email)
    return message


def validate_students(students):
    from grading.models import students_count
    students_list = students.split(',')
    if len(students_list) != students_count(students_list):
        return 'invalid students'
    return ''


# def validate_course_id(course):
#     from grading.models import get_students
#     students_list = students.split(',')
#     ids = get_students(students_list)
#     if len(students_list) != len(ids):
#         return 'invalid students'
#     return ''


def validate_course(name, students):
    if not name:
        message = 'missing name'
    elif not students:
        message = 'missing students'
    else:
        message = validate_students(students)
    return message


def validate_grade(grade, student, course):
    if not grade:
        message = 'missing grade'
    elif not student:
        message = 'missing student'
    elif not course:
        message = 'missing course'
    else:
        message = validate_grade_range(grade)
    # else:
    #     message = validate_students([student])
    #     if not message:
    #         message = validate_course_id(course)
    return message


def validate_grade_range(grade):
    if grade < 0 or grade > 100:
        return 'grade out of range'
    return ''