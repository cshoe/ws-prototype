from tornado import httpserver, ioloop, web

from handlers import *

application = web.Application([
    (r'/', MainHandler),
    (r'/msg', MessagePubHandler),
    (r'/ws/track', MessageSubHandler),
    (r'/static/(.*)', NoCacheStaticFileHandler, {'path': '../static'}),
    (r'/collections/(?P<collection_slug>[a-z0-9-]+)', CollectionPubHandler),
    (r'/ws/collections/(?P<collection_slug>[a-z0-9-]+)', CollectionSubHandler),
])

if __name__ == '__main__':
    server = httpserver.HTTPServer(application)
    server.listen(8888)
    ioloop.IOLoop.instance().start()
