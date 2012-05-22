import datetime
import mimetypes
import os


from tornado import gen, web, websocket
import tornadoredis


c = tornadoredis.Client()
c.connect()


class MainHandler(web.RequestHandler):
    """
    Render homepage.

    """
    def get(self):
        self.render('../templates/index.html')


class MessagePubHandler(web.RequestHandler):
    """
    Post a new message to the `message_channel` in redis.

    """
    def post(self):
        message = self.get_argument('message')
        c.publish('message_channel', message)
        self.set_header('Content-Type', 'text/plain')
        self.write('sent: {}'.format(message))


class MessageSubHandler(websocket.WebSocketHandler):
    """
    Listen to the the `message_channel` on redis.

    """

    def __init__(self, *args, **kwargs):
        super(MessageSubHandler, self).__init__(*args, **kwargs)
        self.listen()

    @gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield gen.Task(self.client.subscribe, 'message_channel')
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))

    def close(self):
        self.client.unsubscribe('message_channel')
        self.client.disconnect()


class CollectionPubHandler(web.RequestHandler):
    """
    Publish that a number of new items has been received.

    """
    def get(self, collection_slug):
        self.render('../templates/collection.html', slug=collection_slug)

    def post(self, collection_slug):
        item_count = self.get_argument('items')
        c.publish('collection_channel_{}'.format(collection_slug), item_count)
        self.set_header('Content-Type', 'text/plain')
        self.write('published {} items to {}'.format(item_count,
            collection_slug))


class CollectionSubHandler(websocket.WebSocketHandler):
    """

    """
    def open(self, collection_slug):
        self.collection_slug = collection_slug
        self.listen()

    @gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield gen.Task(self.client.subscribe,
            'collection_channel_{}'.format(self.collection_slug))
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))

    def close(self):
        self.client.unsubscribe(
            'collection_channel_{}'.format(self.collection_slug))
        self.client.disconnect()


class NoCacheStaticFileHandler(web.StaticFileHandler):
    """
    Same as Tornado's :py:class:`StaticFileHandler` but never caches anything.

    Courtesy of robmadole.

    """
    def get(self, path, include_body=True):
        """
        See :py:method:`tornado.web.StaticFileHandler.get()`.

        This will always read the file and return a 200, never a 304.
        """
        path = self.parse_url_path(path)
        abspath = os.path.abspath(os.path.join(self.root, path))
        if not (abspath + os.path.sep).startswith(self.root):
            raise web.HTTPError(403, "%s is not in root static directory",
                path)
        if os.path.isdir(abspath) and self.default_filename is not None:
            if not self.request.path.endswith("/"):
                self.redirect(self.request.path + "/")
                return
            abspath = os.path.join(abspath, self.default_filename)
        if not os.path.exists(abspath):
            raise web.HTTPError(404)
        if not os.path.isfile(abspath):
            raise web.HTTPError(403, "%s is not a file", path)

        mime_type, encoding = mimetypes.guess_type(abspath)
        if mime_type:
            self.set_header("Content-Type", mime_type)

        self.set_header("Expires", datetime.datetime.utcnow())
        self.set_header("Cache-Control", "max-age=-1")

        self.set_extra_headers(path)

        with open(abspath, "rb") as file:
            data = file.read()
            if include_body:
                self.write(data)
            else:
                assert self.request.method == "HEAD"
                self.set_header("Content-Length", len(data))
