import supervisor.xmlrpc
from xmlrpc.client import ServerProxy


class Supervisor_:

    @classmethod
    def client(cls, simple: bool = True):
        server = ServerProxy('http://127.0.0.1', transport=supervisor.xmlrpc.SupervisorTransport(
            None, None, 'unix:///tmp/supervisor.sock'))
        if simple:
            return server.supervisor
        return server
