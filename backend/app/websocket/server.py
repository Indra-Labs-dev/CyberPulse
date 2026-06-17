import socketio

from app.websocket.manager import sio


def create_socket_app(other_asgi_app) -> socketio.ASGIApp:
    return socketio.ASGIApp(sio, other_asgi_app=other_asgi_app, socketio_path="socket.io")
