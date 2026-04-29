from app import create_app
from config import settings


flask_app = create_app()


if __name__ == "__main__":
    flask_app.run(host=settings.host, port=settings.port, debug=settings.debug)