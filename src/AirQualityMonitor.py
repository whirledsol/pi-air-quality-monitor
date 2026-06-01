import json
import os
import time
from datetime import datetime,timezone,timedelta
import serial
import redis
import aqi

redis_client = redis.StrictRedis(host=os.environ.get('REDIS_HOST'), port=6379, db=0)


class AirQualityMonitor():

    def __init__(self, serialPath):
        """constructor"""
        self.ser = serial.Serial(serialPath)

    def get_measurement(self):
        """read live measurement from serial"""
        self.data = []
        for index in range(0,10):
            datum = self.ser.read()
            self.data.append(datum)
        self.pmtwo = int.from_bytes(b''.join(self.data[2:4]), byteorder='little') / 10
        self.pmten = int.from_bytes(b''.join(self.data[4:6]), byteorder='little') / 10
        self.aqi = aqi.to_aqi([(aqi.POLLUTANT_PM25, str(self.pmtwo)),
                            (aqi.POLLUTANT_PM10, str(self.pmten))
                            (aqi.POLLUTANT_O3_8H, '1') #static because not recorded but needed to make the aqi algorithm make sense
                            ])
        self.aqi = float(self.aqi)

        self.meas = {
            "pm2.5": self.pmtwo,
            "pm10": self.pmten,
            "aqi": self.aqi,
        }
        return {
            "timestamp": datetime.now(timezone.utc),
            'measurement': self.meas
        }


    def save_measurement_to_redis(self):
        """Saves measurement to redis db"""
        redis_client.lpush('measurements', json.dumps(self.get_measurement(), default=str))

    def get_redis_measurements(self):
        """just gets all the data"""
        return [json.loads(x) for x in redis_client.lrange('measurements', 0, -1)]

    def query_data(self, startDate = None, granularity = 1):
        """get data based on parameters"""
        #default startDate = 24 hours ago
        print('getData',startDate,granularity)
        startDate = datetime.now(timezone.utc) - timedelta(hours=24) if startDate is None else startDate
        print("StartDate",startDate)
        data = self.get_redis_measurements()
        print('data length',len(data))
        return data

