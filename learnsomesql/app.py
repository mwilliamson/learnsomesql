import flask
import os


def create_app(lessons):
    app = flask.Flask(
        "learnsomesql",
        template_folder=_package_path("templates"),
        static_folder=_package_path("static"),
    )

    @app.route("/")
    def hello():
        return "Hello World!"
    
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
        
    return app
    

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
    create_app(sample_lessons).run(debug=True)

