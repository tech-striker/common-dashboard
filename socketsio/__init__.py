from flask_socketio import SocketIO
import eventlet

socketio = SocketIO( cors_allowed_origins="+")


def create_socketio(app):
    from . import chat_events

    async_mode = 'eventlet'
    socketio.init_app(app, async_mode=async_mode,  cors_allowed_origins="*")
    return app
