from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer
from io import BytesIO
from socket import error as socket_error

from errors import Disconnect, CommandError, Error
from server.protocol_handler import ProtocolHandler


class Server(object):
    def __init__(self, host="127.0.0.1", port=31337, max_clients=64) -> None:
        self._pool = Pool(max_clients)
        self._sever = StreamServer(
            (host, port), self.connection_handler, spawn=self._pool
        )

        self._protocol = ProtocolHandler()
        self._kv = {}

    def connection_handler(self, conn, address):
        socket_file = conn.makefile("rwb")

        while True:
            try:
                data = self._protocol.handle_request(socket_file)
            except Disconnect:
                break

            try:
                resp = self.get_response(data)
            except CommandError as exc:
                resp = Error(exc.args[0])

        self._protocol.write_response(socket_file, resp)

    def get_response(self, data):
        pass

    def run(self):
        self._sever.serve_forever()
