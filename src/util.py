
import pytz
import tzlocal
import time
import os
import configparser
from datetime import datetime

def parse_config():
    """create or read from app.ini file"""
    CONFIG_FILE_NAME = './app.ini'
    config = configparser.ConfigParser()
    if(os.path.isfile(CONFIG_FILE_NAME)):
        config.read(CONFIG_FILE_NAME)
        return config
    else:
        config['DEFAULT'] = {'MeasureIntervalSeconds': '60', #take measurement every n seconds
                     'serialPath': "/dev/ttyUSB0"
        }
        with open(CONFIG_FILE_NAME, 'w') as configfile:
            config.write(configfile)
        return config


def pretty_timestamps(measurement):
	timestamps = []
	for x in measurement:
		timestamp = x['timestamp']
		timestamps += [timestamp.split('.')[0]]
	return timestamps


def parse_timestamp(timestampstr):
    '''
    parse timestamp
    '''
    return datetime.strptime(timestampstr,"%Y-%m-%d %H:%M:%S.%f%z")


def reconfigure_data(measurement):
    """Reconfigures data for chart.js"""
    return {
        'labels': pretty_timestamps(measurement),
        'aqi': {
            'label': 'aqi',
            'data': [x['measurement']['aqi'] for x in measurement],
            'backgroundColor': '#181d27',
            'borderColor': '#181d27',
            'borderWidth': 3,
        },
        'pm10': {
            'label': 'pm10',
            'data': [x['measurement']['pm10'] for x in measurement],
            'backgroundColor': '#cc0000',
            'borderColor': '#cc0000',
            'borderWidth': 3,
        },
        'pm2': {
            'label': 'pm2.5',
            'data': [x['measurement']['pm2.5'] for x in measurement],
            'backgroundColor': '#42C0FB',
            'borderColor': '#42C0FB',
            'borderWidth': 3,
        },
    }

def convert_datetime_local(dt):
    """converts the timestamp to local"""
    # get local timezone    
    local_tz = tzlocal.get_localzone() 
    print(f'Your timezone is {local_tz}.')
    return local_tz.localize(dt)

def chunks(l, n):
    '''
    list to list of lists of size n
    '''
    newList = []

    for i in range(0, len(l), n):
        newList.append(l[i:i+n])
    return newList
