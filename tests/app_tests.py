from nose.tools import istest, assert_equal, assert_in, assert_not_in

from learnsomesql.app import create_app, Lesson



@istest
def root_page_redirects_to_first_lesson():
    client = _create_client()
    response = client.get("/")
    assert_equal(302, response.status_code)
    assert_equal("http://localhost/lesson/simple-selects", response.headers["location"])
    

@istest
def lesson_slug_is_used_to_find_lesson():
    client = _create_client()
    response = client.get("/lesson/select-star")
    assert_equal(200, response.status_code)
    assert_in("<h2>SELECT *</h2>", response.data)
    
    
@istest
def next_lesson_is_shown_if_not_last_lesson():
    client = _create_client()
    response = client.get("/lesson/select-star")
    assert_in("<h2>Next lesson: WHERE clauses</h2>", response.data)
    
    
@istest
def next_lesson_is_not_shown_if_last_lesson():
    client = _create_client()
    response = client.get("/lesson/where-clauses")
    assert_not_in("<h2>Next lesson", response.data)


@istest
def unknown_lesson_returns_404():
    client = _create_client()
    response = client.get("/lesson/bwah")


def _create_client():
    lessons = [
        Lesson("simple-selects", "Simple SELECTs", "<p>SELECTs are simple</p>"),
        Lesson("select-star", "SELECT *", "<p>Don't use SELECT * in code</p>"),
        Lesson("where-clauses", "WHERE clauses", "<p>This is a WHERE clause</p>"),
    ]
    app = create_app(lessons)
    return app.test_client()
    
