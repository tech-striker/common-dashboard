# flask packages
from flask import Flask, app
from flask_restful import Api
from flask_mongoengine import MongoEngine
# from flask_jwt_extended import JWTManager
from authentication.routes import create_authentication_routes
import os
from flask_mail import Mail
from socketsio import create_socketio, socketio

# init mongoengine
db = MongoEngine()

# init jwt manager
# jwt = JWTManager()


# init flask mail
mail = Mail()

from dotenv import load_dotenv

load_dotenv()

# default mongodb configuration
default_config = {
    'MONGODB_SETTINGS': {
        'db': os.environ['DB_NAME'],
        'host': os.environ['DB_HOST'],
        'port': int(os.environ['DB_PORT']),
        'username': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'authentication_source': 'admin'
    },
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 465,
    'MAIL_USERNAME': 'nkcse0007@gmail.com',
    'MAIL_PASSWORD': 'Bond007@#1996',
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': True,
    'SECRET_KEY': os.environ.get('SECRET_KEY'),
    'JWT_SECRET_KEY': os.environ['JWT_SECRET_KEY']
}


def get_flask_app(config: dict = None) -> app.Flask:
    """
    Initializes Flask app with given configuration.
    Main entry point for wsgi (gunicorn) server.
    :param config: Configuration dictionary
    :return: app
    """
    # init flask
    flask_app = Flask(__name__)

    # configure app
    config = default_config if config is None else config
    flask_app.config.update(config)

    # load config variables
    if 'MONGODB_URI' in os.environ:
        flask_app.config['MONGODB_SETTINGS'] = {'host': os.environ['MONGODB_URI'],
                                                'retryWrites': False}
    if 'JWT_SECRET_KEY' in os.environ:
        flask_app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

    # init api and routes
    api = Api(app=flask_app)
    create_authentication_routes(api=api)
    from chat.routes import create_chat_routes
    create_chat_routes(api=api)

    db.init_app(flask_app)

    # jwt.init_app(flask_app)

    mail.init_app(flask_app)

    # socket.init_app(flask_app)

    return flask_app


if __name__ == '__main__':
    # Main entry point when run in stand-alone mode.

    app = get_flask_app()
    # app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    # socketio = SocketIO(app, debug=True)

    # app = get_flask_app()
    create_socketio(app)
    socketio.run(app, host='127.0.0.1', debug=True)
