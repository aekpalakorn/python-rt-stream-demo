#!/usr/bin/python
import datetime as dt

import matplotlib
import matplotlib.dates as md
import matplotlib.pyplot as plt
import os
import pandas as pd
import redis
import settings
import tornado.web
import tornado.websocket
from functools import partial
from tornado.options import logging


LISTENERS = {
	'ws': []
}

r = redis.Redis()

'''
Listening to a specified Redis channel
'''
def redis_listener():
	try:
		ps = r.pubsub()
		ps.subscribe(settings.REDIS['channel'])
		io_loop = tornado.ioloop.IOLoop.instance()
		for message in ps.listen():		
			for socket in LISTENERS['ws']:
				io_loop.add_callback(partial(socket.on_message,message))
	# Note: Not sure if this block will be reached at all
	except:
		logging.info('redis_listener() aborted. Stop subscribing.')
		ps.close()

def plot(timeseries,fig_name):
    matplotlib.rc('font', **settings.PLOT['font'])
    plt.figure(figsize=(14,2.5), dpi=72)	
    ax = plt.subplot(1,1,1)  
    rts = pd.rolling_mean(timeseries, settings.PLOT['rolling_mean_min'])
    plt.plot(rts.index, rts.values, settings.PLOT['fill'])
    plt.ylabel('Tweets per minute (TPM)')
    ax.fill_between(rts.index, rts.values, 0, color=settings.PLOT['fill'])
    ax.xaxis.set_major_locator(md.HourLocator(interval=settings.PLOT['xaxis_interval_hr']))
    ax.xaxis.set_major_formatter(md.DateFormatter(settings.PLOT['datetime_format']))
    ax.autoscale_view()
    plt.grid(True)
    plt.xlabel('Time (SGT)')
    fig = os.path.join(settings.SERVER['static_files_path'],'images',fig_name)
    plt.savefig(fig,bbox_inches='tight')
    logging.info('Saving %s' % fig)

class WebHandler(tornado.web.RequestHandler):
	def get(self):
		self.render(settings.TEMPLATE_FILENAME)

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		LISTENERS['ws'].append(self)
		logging.info('WebSocket connected to client no. %s' % len(LISTENERS['ws']))
	
	'''
	Upon receiving a specific notification from Redis:
	1. Look up the time series data in Redis store.
	2. Generate and save the plot using matplotlib
	3. Notify the web client that a plot is ready
	'''
	def on_message(self,message):
		if message['data'] == settings.REDIS['message']:
			fig_name = 'cur_tpm_sg.png'
			index = r.lrange(settings.REDIS['key_index'],0,-1)
			vals = r.lrange(settings.REDIS['key_values'],0,-1)
			dates = [dt.datetime.strptime(x, settings.REST['datetime_format'])+dt.timedelta(hours=8) for x in index] # Convert GMT to SGT
			ts = pd.Series(vals, dates)
			plot(ts,fig_name)
			self.write_message(fig_name)

	def on_close(self):
		LISTENERS['ws'].remove(self)
		logging.info('WebSocket disconnected!')
