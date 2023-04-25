import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
import redis
import atexit
import configparser
import pytz
import tzlocal
from AirQualityMonitor import AirQualityMonitor
from FlaskClient import FlaskClient

# application

def main():
    #config
    config = parse_config()

    #hardware
    aqm = AirQualityMonitor()

    #logging
    scheduler = BackgroundScheduler()
    measureIntervalSeconds = config['DEFAULT']['MeasureIntervalSeconds']
    scheduler.add_job(func=aqm.save_measurement_to_redis, trigger="interval", seconds=measureIntervalSeconds)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    
    client = FlaskClient()


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

def convert_datetime_local(dt):
    """converts the timestamp to local"""
    # get local timezone    
    local_tz = tzlocal.get_localzone() 
    print(f'Your timezone is {local_tz}.')
    return local_tz.localize(dt)


def reconfigure_data(measurement):
    """Reconfigures data for chart.js"""
    current = int(time.time())
    measurement = measurement[:30]
    measurement.reverse()
    return {
        'labels': [x['measurement']['timestamp'] for x in measurement],
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


if __name__ == "__main__":
    main()