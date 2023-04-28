
import pytz
import tzlocal
import time
import os
import configparser

def parse_config():
    """create or read from app.ini file"""
    CONFIG_FILE_NAME = './app.ini'
    config = configparser.ConfigParser()
    if(os.path.isfile(CONFIG_FILE_NAME)):
        config.read(CONFIG_FILE_NAME)
        return config
    else:
        config['DEFAULT'] = {'MeasureIntervalSeconds': '60', #take measurement every n seconds
                     'AverageMeasurements': '5', #average n measurements before saving to redis and take latest timestamp TODO
                     'InitialGridRangeCount': '30' #in the UI, initially show a max of measurements
        }
        with open(CONFIG_FILE_NAME, 'w') as configfile:
            config.write(configfile)
        return config



def reconfigure_data(measurements):
        """Reconfigures data for chart.js"""
        current = int(time.time())
        measurements = measurements[:30]
        measurements.reverse()
        return {
            'labels': [x['measurement']['timestamp'] for x in measurements],
            'aqi': {
                'label': 'aqi',
                'data': [x['measurement']['aqi'] for x in measurements],
                'backgroundColor': '#181d27',
                'borderColor': '#181d27',
                'borderWidth': 3,
            },
            'pm10': {
                'label': 'pm10',
                'data': [x['measurement']['pm10'] for x in measurements],
                'backgroundColor': '#cc0000',
                'borderColor': '#cc0000',
                'borderWidth': 3,
            },
            'pm2': {
                'label': 'pm2.5',
                'data': [x['measurement']['pm2.5'] for x in measurements],
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
    return local_tz.localize(dt)30