from tornado import httpserver, ioloop, web

from tornadio2 import server, TornadioRouter

from seperate_servers.handlers import IndexHandler
from seperate_servers.sockets import StreamRouter, MessageHandler

http_application = web.Application([
    (r'/static/(.*)', web.StaticFileHandler, {'path': '../static'}),
    (r'/js/(.*)', web.StaticFileHandler, {'path': 'js'}),
    (r'/', IndexHandler)
])

if __name__ == "__main__":
    http_server = httpserver.HTTPServer(http_application)
    http_server.listen(8080)
    
    stream_router = TornadioRouter(StreamRouter, namespace='stream')
    user_router = TornadioRouter(MessageHandler, namespace='message')

    socket_app = web.Application(stream_router.urls + user_router.urls,
        socket_io_port=8082)
    socket_server = server.SocketServer(socket_app, auto_start=False)

    ioloop.IOLoop.instance().start()
