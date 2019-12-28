import json

import pytest
from flask_api import status

from tests.conftest import valid_credentials, create_student, create_course, create_grade


@pytest.mark.parametrize("data, expected", [
    (('John', 'Cleese', 'jc@mp.com'), (status.HTTP_201_CREATED)),
])
def test_student_success(data, expected, clean_db, flask_client):
    res = flask_client.post('/student', json=dict(
        first_name=data[0],
        second_name=data[1],
        email=data[2]
    ), follow_redirects=True, headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == expected


@pytest.mark.parametrize("data, expected", [
    (('', 'Cleese', 'jc@mp.com'), (status.HTTP_400_BAD_REQUEST, 'missing first name')),
    (('John', '', 'jc@mp.com'), (status.HTTP_400_BAD_REQUEST, 'missing second name')),
    (('John', 'Cleese', ''), (status.HTTP_400_BAD_REQUEST, 'missing email')),
    (('John', 'Cleese', 'jc&mp.com'), (status.HTTP_400_BAD_REQUEST, 'email not valid')),
])
def test_student_fail(data, expected, clean_db, flask_client):
    res = flask_client.post('/student', json=dict(
        first_name=data[0],
        second_name=data[1],
        email=data[2]
    ), follow_redirects=True, headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == expected[0]
    assert res.data.decode("utf-8") == expected[1]


def test_duplicate_student(clean_db, flask_client):
    create_student(flask_client,
                   first_name='John',
                   second_name='Cleese',
                   email='jc@mp.com')
    res = flask_client.post('/student',
                            json=dict(first_name='John',
                                      second_name='Cleese',
                                      email='jc@mp.com'),
                            follow_redirects=True,
                            headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_409_CONFLICT


def test_delete_student(clean_db, flask_client):
    id = create_student(flask_client)
    res = flask_client.delete(f'/student/{id}', follow_redirects=True, headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_204_NO_CONTENT
    id = create_student(flask_client)
    path = f'/student/{id+1}'
    res = flask_client.delete(path, follow_redirects=True, headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_404_NOT_FOUND


def test_get_student(clean_db, flask_client):
    id = create_student(flask_client)
    res = flask_client.get(f'/student/{id}',
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK


def test_update_student(clean_db, flask_client):
    id = create_student(flask_client)
    res = flask_client.put(f'/student/{id}',
                           json=dict(first_name='Jhn',
                                     second_name='Cleese',
                                     email='jc@mp.com'),
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK


def test_course_success(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    create_course(flask_client, [str(id1), str(id2)])


def test_course_update(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id = create_course(flask_client, [str(id1), str(id2)])
    res = flask_client.put(f'/course/{course_id}',
                           json=dict(name='history',
                                     students=','.join([str(id1)])),
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK


def test_course_get_delete(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id = create_course(flask_client, [str(id1), str(id2)])
    res = flask_client.get(f'/course/{course_id}',
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK
    res = flask_client.delete(f'/course/{course_id}',
                              follow_redirects=True,
                              headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_204_NO_CONTENT


def test_add_grade(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id = create_course(flask_client, [str(id1), str(id2)])
    res = create_grade(flask_client, 70, course_id, id1)
    assert res._status_code == status.HTTP_201_CREATED
    res = create_grade(flask_client, 80, course_id, '44')
    assert res._status_code == status.HTTP_400_BAD_REQUEST


def test_update_grade(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id = create_course(flask_client, [str(id1), str(id2)])
    res = create_grade(flask_client, 70, course_id, id1)
    assert res._status_code == status.HTTP_201_CREATED
    res = flask_client.put('/grade',
                            json=dict(grade=60,
                                      student=str(id1),
                                      course=course_id),
                            follow_redirects=True,
                            headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK


def test_get_delete_grade(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id = create_course(flask_client, [str(id1), str(id2)])
    create_grade(flask_client, 70, course_id, id1)
    res = flask_client.get(f'/grade/{id1}/{course_id}',
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK
    res = flask_client.delete(f'/grade/{id1}/{course_id}',
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_204_NO_CONTENT


def test_get_grades(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id = create_course(flask_client, [str(id1), str(id2)])
    create_grade(flask_client, 70, course_id, id1)
    create_grade(flask_client, 77, course_id, id2)
    res = flask_client.get(f'/grade',
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK


def test_best_student(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id = create_course(flask_client, [str(id1), str(id2)])
    create_grade(flask_client, 70, course_id, id1)
    create_grade(flask_client, 77, course_id, id2)
    res = flask_client.get(f'/best_student',
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK


def test_easy_course(clean_db, flask_client):
    id1 = create_student(flask_client)
    id2 = create_student(flask_client, first_name='C', second_name='D', email='c@d.com')
    course_id1 = create_course(flask_client, [str(id1), str(id2)])
    course_id2 = create_course(flask_client, [str(id1), str(id2)], name='history')
    create_grade(flask_client, 70, course_id1, id1)
    create_grade(flask_client, 77, course_id1, id2)
    create_grade(flask_client, 70, course_id2, id1)
    create_grade(flask_client, 76, course_id2, id2)
    res = flask_client.get(f'/easy_course',
                           follow_redirects=True,
                           headers={'Authorization': 'Basic ' + valid_credentials})
    assert res._status_code == status.HTTP_200_OK
    result = res.data.decode()
    course_name = json.loads(result)['name']
    assert course_name == 'history'