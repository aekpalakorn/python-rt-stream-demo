#!/usr/bin/python 
'''
1. Poll real-time tweet stream data of a specified length (past N hours) via REST API
2. Insert time series data into Redis store. The data are stored into 2 lists: datetime index and tweets per minute counts
3. Publish notification to a specified channel

Arguments:
* Data length in hours 
* Polling frequency in seconds
'''
import datetime as dt
from time import sleep

import logging
import redis
import simplejson as json
import urllib2 as ul
import sys

# Local settings
LOG_FILENAME = '/home/aek/logs/poller.log'
API_ENDPOINT = 'http://research.larc.smu.edu.sg:8080/PalanteerDevApi/rest/v1/tweets/timeseries'
REDIS = {
    'host': '10.0.106.64',
    'port': 6379,
    'channel': 'test',
    'message': 'tpm_sg_fetched',
    'key_index': 'cur_tpm:sg:index',
    'key_values': 'cur_tpm:sg:values',
}
REST = {
    'key_index': 'timeStr',
    'key_value': 'count',
    'datetime_format': '%Y-%m-%dT%H:%M:%SZ',
}

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
# End settings

def poll(num_hrs):
    cur = dt.datetime.now()
    cur_gmt = cur - dt.timedelta(hours=8)
    url = API_ENDPOINT + '?start=' + (dt.datetime.strftime(cur_gmt-dt.timedelta(hours=num_hrs),REST['datetime_format'])) + '&end=' + (dt.datetime.strftime(cur_gmt,REST['datetime_format'])) + '&timeRange=1m'
    logging.info('Fetching data from %s' % url)
    try:
        response = ul.urlopen(url)
        body = json.loads(response.read())
        js_data = body['data']
        response.close()
        return js_data
    except ul.HTTPError, e:
        logging.error('HTTPError: %s' % str(e.code))
        return None
    except ul.URLError, e:
        logging.error('URLError: %s' % str(e.reason))
        return None
    except Exception:
        import traceback
        logging.error('Generic Exception: %s' % traceback.format_exc())
        return None

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Must provide two positive integers ((1) data length in hours; and (2) polling frequency in seconds.')

    r = redis.Redis(host=REDIS['host'], port=REDIS['port'])

    while True:
        try:
            js_data = poll(int(sys.argv[1]))

            if js_data is not None:
                # Insert data into Redis
                r.delete(REDIS['key_index'])
                r.delete(REDIS['key_values'])
                for d in js_data:
                    r.rpush(REDIS['key_index'], d[REST['key_index']])
                    r.rpush(REDIS['key_values'], int(d[REST['key_value']]))
                r.publish(REDIS['channel'], REDIS['message']) # Publish notification
                logging.info('Published to Redis\' channel %s' % REDIS['channel'])
        except KeyboardInterrupt:
            logging.info('Aborting via KeyboardInterrupt')
            sys.exit()
        except:
            import traceback
            logging.error('Generic Exception: %s' % traceback.format_exc())
            sys.exit()
        sleep(int(sys.argv[2]))
