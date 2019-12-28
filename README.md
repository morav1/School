Project Blaze School environment variables are defined in connfiguration.py

DB and REDIS host can be defined by that.
Tables are set on startup only so DB should be up before app
API access is defined by

--- basic auth username / passwords ---
ALLOWED_CREDENTIALS:
        '{"johnc": "eggs",
          "erici": "spam"}'

CRUD are available for 3 models except for get all students and get all courses
APIs are defined in app.py
port is 5000

example for add student:
url - http://192.168.99.100:5000/student
body - {"id": 531, "first_name": "briaddn", "second_name": "superstar", "email": "the@fife.of"}

additional methods:
/best_student
/easy_course

redis lock is implemented
redis cache is not
