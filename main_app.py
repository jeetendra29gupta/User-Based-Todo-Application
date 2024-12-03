import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask

from models import init_db
from todo_route import todo_router
from user_route import user_router


def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "Secret_Key-2024"),
        SESSION_PERMANENT=bool(os.getenv("SESSION_PERMANENT", True)),
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=int(os.getenv("PERMANENT_SESSION_LIFETIME", 30)))
    )

    with app.app_context():
        init_db()

    app.register_blueprint(user_router)
    app.register_blueprint(todo_router)

    return app


if __name__ == '__main__':
    todo_app = create_app()
    todo_app.run(host='0.0.0.0', port=8181, debug=True)
