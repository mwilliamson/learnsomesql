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


    @app.route("/lesson")
    def lesson():
        return flask.render_template("lesson.html")
        
    return app
    
    
def _package_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", path))


if __name__ == "__main__":
    create_app().run(debug=True)

