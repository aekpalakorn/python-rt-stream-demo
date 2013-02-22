Real-Time Streaming Demo
========================

Monitoring tweet streaming data via a REST API source in real-time using Tornado, WebSocket, and Redis. 

The demo has been tested in Ubuntu 12.04 and CentOS 6.2.

Required
--------

* Python
* Tornado
* Pandas (for time series and plotting functions)
* Redis

How to run
----------

1. Open and edit settings.py. Make sure there is Redis server running. PalanteerDev REST API will be used in the demo.

2. Start a poller program with two arguments, for example:

	python poller.py 12 60

This will instruct the poller to make a request to a specified REST API every 60 seconds to get the last 12 hours of tweets per minute (TPM) counts. Once the data has been obtained, the poller will push 2 lists into Redis for the time series' index (datetimes in ISO format) and values (TPM counts) and publish a notification to a specified Redis channel.

3. Start a server:

	python server.py

The server will listen to the specified Redis channel. Once a new notificiation has been published, a new time series plot will be generated and saved in a predefined static files folder. Next, a WebSocket handler will notify a web client of the new image file.

4. Open a Chrome browser and access the following URL (as configured in server.py):
	
	http://10.0.106.64/stream

Look at Chrome's console for WebSocket updates. The time series plot should be updated every minute.

To do
-----

* New Feature: Revamped web front-end real-time visualization UI. Possible implementation in cubism (https://github.com/square/cubism), graphite (http://graphite.readthedocs.org/en/latest/), or envision.js (http://www.humblesoftware.com/envision/demos/realtime).
