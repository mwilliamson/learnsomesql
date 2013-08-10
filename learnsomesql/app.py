import flask
import os


def create_app():
    app = flask.Flask(
        "learnsomesql",
        template_folder=_package_path("templates"),
        static_folder=_package_path("static"),
    )

    @app.route("/")
    def hello():
        return "Hello World!"

    
    lessons = [
        Lesson("simple-selects", "Simple SELECTs"),
        Lesson("select-star", "SELECT *"),
    ]
    
    def _find_lesson(slug):
        for lesson in lessons:
            if lesson.slug == slug:
                return lesson
        
    
    @app.route("/lesson/<lesson_slug>")
    def lesson(lesson_slug):
        lesson = _find_lesson(lesson_slug)
        return flask.render_template("lesson.html", lesson=lesson)
        
    return app
    

class Lesson(object):
    def __init__(self, slug, name):
        self.slug = slug
        self.name = name

    
def _package_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", path))


if __name__ == "__main__":
    create_app().run(debug=True)

