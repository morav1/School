import base64
import json

from flask_api import status
from pytest import fixture

from grading import models
from app import db, app
from grading.models import create_tables


@fixture(scope='function')
def clean_db():
    create_tables()
    models.Grade.query.delete()
    models.Student.query.delete()
    models.Course.query.delete()
    db.session.commit()


valid_credentials = base64.b64encode(b'johnc:eggs').decode('utf-8')
@fixture(scope='module')
def flask_client():
    return app.test_client()


def create_student(flask_client, first_name='brian', second_name='superstar', email='the@fife.of'):
    res = flask_client.post('/student',
                            json=dict(first_name=first_name,
                                      second_name=second_name,
                                      email=email),
                            follow_redirects=True,
                            headers={'Authorization': 'Basic ' + valid_credentials})
    result = res.data.decode()
    return json.loads(result)['id']


def create_course(flask_client, students, name='math'):
    res = flask_client.post('/course',
                            json=dict(name=name,
                                      students=','.join(students)),
                            follow_redirects=True,
                            headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_201_CREATED
    result = res.data.decode()
    course_id = json.loads(result)['id']
    return course_id


def create_grade(flask_client, grade, course_id, student_id):
    res = flask_client.post('/grade',
                            json=dict(grade=grade,
                                      student=str(student_id),
                                      course=course_id),
                            follow_redirects=True,
                            headers={'Authorization': 'Basic ' + valid_credentials})
    return res


