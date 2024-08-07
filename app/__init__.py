from flask import Flask,url_for
from flask_sqlalchemy import SQLAlchemy
from .routes import example


db = SQLAlchemy()

def create_app():
    app = Flask(__name__,template_folder="template",static_folder="static")
    app.config.from_object('app.config.Config')
    app.register_blueprint(example)


    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes here to avoid circular import
        db.create_all()
    
    # Define before_request hook here
    @app.before_request
    def before_request_func():
        print("This runs before every request")
        print (app.url_map)
    return app
