# Dependencies
import time, logging
import src.DAQ as daq

def main():
    logger = logging.getLogger(__name__)
    initLogger(logger, format='[ %(asctime)s %(module)5s:%(funcName)-15s ] %(message)s')
    DAQ = daq.DAQ(logger)
    DAQ.loadConfig('cfg/config.ini')
    DAQ.initI2C()
    DAQ.initSensors()

    prevTime = 0
    sampleRate = 100 # Hz
    dt = 1 / sampleRate # Seconds
    while True:
        try:
            accel = DAQ.getAccel()
            gyro = DAQ.getGyro()
            mag = DAQ.getMag()
            temp = DAQ.getTemperature()
            pressure = DAQ.getPressure()
            altitude = DAQ.getAltitudeBMP280()
        except Exception as ex:
            logger.debug("Failure while fetching data from DAQ!")
            raise ex

        # Wait for next sample period
        while time.time() - prevTime < dt:
            pass

        prevTime = time.time()

def initLogger(logger, format):
    logging.basicConfig(format=format)
    logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    main()