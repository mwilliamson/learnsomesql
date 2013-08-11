import os
import contextlib
import json

import flask
import sqlexecutor
from sqlexecutor.results import ResultTable

from learnsomesql.courses import CourseReader


@contextlib.contextmanager
def create_app(course, dialect):
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
                next_lesson_json = {"title": next_lesson.title, "url": next_lesson.url}
            else:
                next_lesson = None
                next_lesson_json = None
            
            question_json = json.dumps({
                "questions": map(question_to_json, lesson.questions),
                "nextLesson": next_lesson_json
            })
            
            return flask.render_template(
                "lesson.html",
                lesson=lesson,
                next_lesson=next_lesson,
                all_lessons=all_lessons,
                question_json=question_json,
            )
            
    def question_to_json(question):
        return {
            "description": question.description,
            "correctAnswer": question.correct_query,
            "expectedResults": {
                "columnNames": question.expected_results.column_names,
                "rows": question.expected_results.rows
            }
        }
    
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
    
    sqlexecutor.prepare(dialect, None)
    
    executor = sqlexecutor.executor(dialect, None)
    try:
        yield app
    finally:
        executor.close()


class LessonViewModel(object):
    def __init__(self, lesson):
        self.title = lesson.title
        self.url = flask.url_for("lesson", lesson_slug=lesson.slug)
        self.description = lesson.description
        self.questions = lesson.questions

    
def _package_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", path))


if __name__ == "__main__":
    dialect = "sqlite3"
    
    sqlexecutor.prepare(dialect, None)
    executor = sqlexecutor.executor(dialect, None)
    
    course_reader = CourseReader(executor)
    this_dir = os.path.dirname(__file__)
    course_path = os.path.join(this_dir, "../courses/sql-select-course.xml")
    course = course_reader.read_file(course_path, dialect)
    
    with create_app(course, dialect) as app:
        app.run(debug=True)

