from flask_socketio import SocketIO, emit, join_room, leave_room


def emit_generate_refund_event(data):
    emit('refund_generated', data)
