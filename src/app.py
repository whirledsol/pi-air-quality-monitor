import os
from apscheduler.schedulers.background import BackgroundScheduler
import redis
import atexit
import configparser
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







if __name__ == "__main__":
    main()