from tornado import web


class IndexHandler(web.RequestHandler):

    def get(self):
        self.render('templates/index.html')
