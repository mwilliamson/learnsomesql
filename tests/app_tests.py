import json
import contextlib

from nose.tools import istest, assert_equal, assert_in, assert_not_in

from learnsomesql.app import create_app, Course, Lesson



@istest
def root_page_redirects_to_first_lesson():
    with _create_client() as client:
        response = client.get("/")
        assert_equal(302, response.status_code)
        assert_equal("http://localhost/lesson/simple-selects", response.headers["location"])
    

@istest
def lesson_slug_is_used_to_find_lesson():
    with _create_client() as client:
        response = client.get("/lesson/select-star")
        assert_equal(200, response.status_code)
        assert_in("<h2>SELECT *</h2>", response.data)
    
    
@istest
def next_lesson_is_shown_if_not_last_lesson():
    with _create_client() as client:
        response = client.get("/lesson/select-star")
        assert_in("<h2>Next lesson: WHERE clauses</h2>", response.data)
    
    
@istest
def next_lesson_is_not_shown_if_last_lesson():
    with _create_client() as client:
        response = client.get("/lesson/where-clauses")
        assert_not_in("<h2>Next lesson", response.data)


@istest
def unknown_lesson_returns_404():
    with _create_client() as client:
        response = client.get("/lesson/bwah")


@istest
def query_returns_result_of_running_query_in_course_context():
    with _create_client() as client:
        response = client.post("/query", data={"query": "SELECT name FROM hats"})
        result = json.loads(response.data)
        assert_equal("SELECT name FROM hats", result["query"])
        assert_equal({"columnNames": ["name"], "rows": [["Fedora"]]}, result["table"])
        assert "error" not in result


@istest
def query_returns_error_if_query_is_malformed():
    with _create_client() as client:
        response = client.post("/query", data={"query": "SELECTEROO"})
        result = json.loads(response.data)
        assert_equal("SELECTEROO", result["query"])
        assert_equal('near "SELECTEROO": syntax error', result["error"])
        assert "table" not in result


@contextlib.contextmanager
def _create_client():
    creation_sql = [
        "create table hats (name);",
        "insert into hats (name) values ('Fedora');",
    ]
    
    lessons = [
        Lesson("simple-selects", "Simple SELECTs", "<p>SELECTs are simple</p>", []),
        Lesson("select-star", "SELECT *", "<p>Don't use SELECT * in code</p>", []),
        Lesson("where-clauses", "WHERE clauses", "<p>This is a WHERE clause</p>", []),
    ]
    course = Course(creation_sql, lessons)
    with create_app(course) as app:
        yield app.test_client()
    
