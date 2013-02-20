# Server-wide settings
SERVER = {
	'log_file_prefix': '/home/aek/logs/tornado',
	'static_files_path': '/home/aek/Projects/python-rt-stream-demo/static',
}

# Redis settings
REDIS = {
    'host': '10.0.106.64',
    'port': 6379,
    'channel': 'test',
    'message': 'tpm_sg_fetched',
    'key_index': 'cur_tpm:sg:index',
    'key_values': 'cur_tpm:sg:values',
}

# REST API response settings
REST = {
    'key_index': 'timeStr',
    'key_value': 'count',
    'datetime_format': '%Y-%m-%dT%H:%M:%SZ',
}

# Template file for /stream handler
TEMPLATE_FILENAME = 'stream.html'

# matplotlib's plot settings
PLOT = {
	'fill': '#00C322',
	'font': {'weight':'normal','size':7},
	'datetime_format': '%b %d,\n %H:%M',
	'xaxis_interval_hr': 1,
	'rolling_mean_min': 5,
}
