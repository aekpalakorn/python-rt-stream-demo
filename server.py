#!/usr/bin/python 
''' 
Tornado server
'''
import os.path
import settings
import stream
import threading
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options, logging


define('port', default=8888, help='run on the given port', type=int)
# Set up logging location
tornado.options.options['log_file_prefix'].set(settings.SERVER['log_file_prefix'])

# Register handlers for each application
handlers = [
	(r'/stream', stream.WebHandler), # Register a handler for real-time TPM
	(r'/ws_stream', stream.WSHandler), # Register a handler for real-time TPM Websocket
	(r'/(.*)', tornado.web.StaticFileHandler, {'path': settings.SERVER['static_files_path']},), # Register a handler for a base directory for static files, e.g., images, scripts, etc.
]
settings = dict(
		template_path=os.path.join(os.path.dirname(__file__),'static/templates'),
		debug='True',
	)
application = tornado.web.Application(handlers,**settings)

# Start HTTP server
if __name__ == '__main__':
	threading.Thread(target=stream.redis_listener).start()

	tornado.options.parse_command_line() # Enable pretty console logging
	logging.info('Starting Tornado server on port %s' % options.port)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
	
	