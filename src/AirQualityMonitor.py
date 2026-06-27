import json
import os
import time
from datetime import datetime, timezone, timedelta
import serial
import redis
import aqi
from statistics import mean
from util import parse_timestamp, chunks
import math
from dateutil import parser

redis_client = redis.StrictRedis(
    host=os.environ.get('REDIS_HOST'), port=6379, db=0)


class AirQualityMonitor():

    def __init__(self, serialPath):
        """constructor"""
        self.ser = serial.Serial(serialPath)

    def get_measurement(self):
        """read live measurement from serial"""
        self.data = []
        for index in range(0, 10):
            datum = self.ser.read()
            self.data.append(datum)

        timestamp = datetime.now(timezone.utc)
        pmtwo = (int.from_bytes(
            b''.join(self.data[2:4]), byteorder='little') / 10) or 0
        pmten = (int.from_bytes(
            b''.join(self.data[4:6]), byteorder='little') / 10) or 0
        myaqi = aqi.to_aqi([
            (aqi.POLLUTANT_PM25, str(pmtwo)),
            (aqi.POLLUTANT_PM10, str(pmten))
        ])
        myaqi = float(myaqi)

        print('get_measurement', pmtwo, pmten)

        return self.build_measurement(timestamp, pmtwo, pmten, myaqi)

    def avg_measurements(self, measurements):
        '''
        avg measurements
        '''
        timestamp = str(max([parse_timestamp(x['timestamp'])
                        for x in measurements]))
        pmtwo = mean([x["measurement"]["pm2.5"] for x in measurements])
        pmten = mean([x["measurement"]["pm10"] for x in measurements])
        myaqi = mean([x["measurement"]["aqi"] for x in measurements])
        return self.build_measurement(timestamp, pmtwo, pmten, myaqi)

    def build_measurement(self, timestamp, pmtwo, pmten, myaqi):
        '''
        builds the model
        '''
        meas = {
            'pm2.5': pmtwo,
            'pm10': pmten,
            'aqi': myaqi
        }
        return {
            'timestamp': timestamp,
            'measurement': meas
        }

    def save_measurement_to_redis(self, measurement=None):
        """Saves measurement to redis db"""
        measurement = measurement or self.get_measurement()
        redis_client.lpush('measurements', json.dumps(measurement, default=str))

    def get_redis_measurements(self):
        """just gets all the data"""
        data = [json.loads(x) for x in redis_client.lrange('measurements', 0, -1)]
        data.reverse()
        return data

    def query_data(self, timeframeHours=12):
        """get data based on parameters"""

        # get all data
        data = self.get_redis_measurements()
        print('raw data length', len(data))


        # clean inputs -- startDate
        timeframeHours = int(timeframeHours)
        print('timeframeHours',timeframeHours,type(timeframeHours))
        startDate = datetime.now(timezone.utc) - timedelta(hours=timeframeHours)

        # filter by startDate
        data = [x for x in data if parse_timestamp(x['timestamp']).timestamp() >= startDate.timestamp()]

        # auto granularity
        MAX_DATA_PTS = 100
        granularity = int(math.ceil(len(data)/MAX_DATA_PTS))

        #show params
        print('getData', startDate, granularity)


        # apply granularity
        if granularity > 1 and len(data) >= granularity:
            bins = chunks(data, granularity)
            data = [self.avg_measurements(bin) for bin in bins]

        # print('data',data)
        print('final data length', len(data))

        return data
