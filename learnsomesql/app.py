import os
import contextlib
import json

import flask
import sqlexecutor
from sqlexecutor.results import ResultTable


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
            "correctAnswer": question.correct_answer,
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
    def __init__(self, slug, title, description, questions):
        self.slug = slug
        self.title = title
        self.description = description
        self.questions = questions


class Question(object):
    def __init__(self, description, correct_answer, expected_results):
        self.description = description
        self.correct_answer = correct_answer
        self.expected_results = expected_results


class LessonViewModel(object):
    def __init__(self, lesson):
        self.title = lesson.title
        self.url = flask.url_for("lesson", lesson_slug=lesson.slug)
        self.description = lesson.description
        self.questions = lesson.questions

    
def _package_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", path))


if __name__ == "__main__":
    creation_sql = [
     """CREATE TABLE cars (
      id int primary key,
      licensePlate text UNIQUE NOT NULL,
      manufacturer text NOT NULL,
      model text NOT NULL,
      color text NOT NULL,
      mileage int NOT NULL,
      brakeHorsepower int NOT NULL
    )""",
    
    "INSERT INTO cars (licensePlate, manufacturer, model, color, mileage, brakeHorsepower) VALUES ('X461 TOM', 'Skoda', 'Fabia', 'red', 64000, 129)",
    
    "INSERT INTO cars (licensePlate, manufacturer, model, color, mileage, brakeHorsepower) VALUES ('FA10 ASM', 'Volkswagen', 'Fox', 'green', 15000, 135)",
    ]
    
    questions = [
        Question(
            description="<p>Get the model of every car in the <code>cars</code> table.</p>",
            correct_answer="SELECT model FROM cars",
            expected_results=ResultTable(
                ["model"],
                [["Fabia"], ["Fox"]],
            ),
        ),
        Question(
            description="<p>Get the color of every car.</p>",
            correct_answer="SELECT color FROM cars",
            expected_results=ResultTable(
                ["color"],
                [["red"], ["green"]],
            ),
        ),
    ]
    
    sample_lessons = [
        Lesson("simple-selects", "Simple SELECTs", "<p>SELECTs are simple</p>", questions),
        Lesson("select-star", "SELECT *", "<p>Don't use SELECT * in code</p>", questions),
    ]
    sample_course = Course(creation_sql, sample_lessons)
    with create_app(sample_course) as app:
        app.run(debug=True)

