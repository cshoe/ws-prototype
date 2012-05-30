import tornadoredis

from tornado import gen
from tornadoio2 import conn


class StreamUpdateHandler(conn.SocketConnection):
    """
    Listen for a number of updates to a stream.

    """

    def on_open(self, info):
        self.channel = 'stream_update'  # redis channel name
        self.listen()

    @gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self.on_message)

    
    def on_message(self, msg):
        # TODO: validate message contents
        if msg.kind == 'message':
            self.send(str(msg.body))

    def close(self):
        self.client.unsubscribe(self.channel)
        self.client.disconnect()


class StreamCreatedHandler(conn.SocketConnection):

    def on_open(self, info):
        self.channel = 'stream_created'  # redis channel name
        self.listen()

    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self.on_message)

    @gen.engine
    def on_message(self, msg):
        if msg.kind == 'message':
            self.send(str(msg.body))

    def close(self):
        self.client.unsubscribe(self.channel)
        self.client.disconnect()


class StreamRouter(conn.SocketConnection):

    __endpoints__ = {'/update': StreamUpdateHandler,
                     '/create': StreamCreatedHandler}

    def on_message(self, msg):
       pass 


class MessageHandler(conn.SocketConnection):

    def on_open(self, info):
        self.channel = 'message'
        self.listen()


    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if msg.kind == 'message':
            self.send(str(msg.body))

    def close(self):
        self.client.unsubscribe(self.channel)
        self.client.disconnect()
