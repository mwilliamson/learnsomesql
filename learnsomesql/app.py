import os
import contextlib

import flask
import sqlexecutor


@contextlib.contextmanager
def create_app(course):
    lessons = course.lessons
    
    app = flask.Flask(
        "learnsomesql",
        template_folder=_package_path("templates"),
        static_folder=_package_path("static"),
    )

    @app.route("/")
    def index():
        return flask.redirect(flask.url_for("lesson", lesson_slug=lessons[0].slug))
    
    
    def _find_lesson_index(slug):
        for index, lesson in enumerate(lessons):
            if lesson.slug == slug:
                return index
                
        return None
    
    
    @app.route("/lesson/<lesson_slug>")
    def lesson(lesson_slug):
        lesson_index = _find_lesson_index(lesson_slug)
        if lesson_index is None:
            return flask.abort(404)
        else:
            all_lessons = map(LessonViewModel, lessons)
            lesson = all_lessons[lesson_index]
            
            if lesson_index + 1 < len(all_lessons):
                next_lesson = all_lessons[lesson_index + 1]
            else:
                next_lesson = None
            
            return flask.render_template(
                "lesson.html",
                lesson=lesson,
                next_lesson=next_lesson,
                all_lessons=all_lessons,
            )
    
    @app.route("/query", methods=["POST"])
    def query():
        query = flask.request.form["query"]
        result = executor.execute(course.creation_sql, query)
        
        response = {
            "query": query
        }
        
        if result.error:
            response["error"] = result.error
            
        if result.table:
            response["table"] = {
                "columnNames": result.table.column_names,
                "rows": result.table.rows
            }
        
        return flask.jsonify(response)
    
    sqlexecutor.prepare("sqlite3", None)
    
    executor = sqlexecutor.executor("sqlite3", None)
    try:
        yield app
    finally:
        executor.close()


class Course(object):
    def __init__(self, creation_sql, lessons):
        self.creation_sql = creation_sql
        self.lessons = lessons


class Lesson(object):
    def __init__(self, slug, title, description):
        self.slug = slug
        self.title = title
        self.description = description
        

class LessonViewModel(object):
    def __init__(self, lesson):
        self.title = lesson.title
        self.url = flask.url_for("lesson", lesson_slug=lesson.slug)
        self.description = lesson.description

    
def _package_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", path))


if __name__ == "__main__":
    sample_lessons = [
        Lesson("simple-selects", "Simple SELECTs", "<p>SELECTs are simple</p>"),
        Lesson("select-star", "SELECT *", "<p>Don't use SELECT * in code</p>"),
    ]
    sample_course = Course([], sample_lessons)
    with create_app(sample_course) as app:
        app.run(debug=True)

