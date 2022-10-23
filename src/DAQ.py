# Dependencies
import board, smbus, configparser
from easydict import EasyDict as edict
import src.NEO6M as neo6m

# Sensor libraries
import adafruit_bmp280
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

class DAQ():
    def __init__(self, logger):
        self.logger = logger
        self.Sensors = edict()
        self.logger.debug("Initialized DAQ")
    
    def initI2C(self):
        self.logger.debug("Initializing I2C bus")
        self.bus = smbus.SMBus(1)
        self.logger.debug("Successfully initialized I2C bus")
    
    def loadConfig(self, path):
        if not hasattr(self, 'cfg'):
            self.cfg = configparser.ConfigParser()
        
        self.cfg.read(path)

    def initSensors(self):
        self.logger.debug("Initializing BMP280")
        self.initBMP280(self.cfg['BMP280'])

        self.logger.debug("Initializing MPU9250")
        self.initMPU9250(self.cfg['MPU9250'])

        self.logger.debug("Initializing NEO6M")
        self.initNEO6M(self.cfg['NEO6M'])
    
    def initBMP280(self, cfg):
        try:
            self.Sensors.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(board.I2C())
            self.Sensors.bmp280.sea_level_pressure = float(cfg['SEALEVEL_PA'])
            self.logger.debug("Set sea level pressure as " + cfg['SEALEVEL_PA'] + " Pa")
        except Exception as ex:
            self.logger.debug("Failure while initializing BMP280!")
            raise ex

    def initMPU9250(self, cfg):
        try:
            self.Sensors.imu = MPU9250(
                    address_ak=eval(cfg['ADDRESS_AK']), 
                    address_mpu_master=eval(cfg['ADDRESS_MASTER']), # 0x68 Address
                    address_mpu_slave=eval(cfg['ADDRESS_SLAVE']), 
                    bus=1,
                    gfs=eval(cfg['GFS']),
                    afs=eval(cfg['AFS']),
                    mfs=eval(cfg['MFS']),
                    mode=eval(cfg['MODE']))
            self.Sensors.imu.configure() # Apply the settings to the registers
            self.logger.debug("AFS Mode: " + cfg['AFS'] + " GFS Mode: " + cfg['GFS'] + " MFS Mode: " + cfg['MFS'])
        except Exception as ex:
            self.logger.debug("Failure while initializing MPU9250!")
            raise ex

    def initNEO6M(self, cfg):
        self.Sensors.gps = neo6m.NEO6M(cfg, self.logger)

    def getAccel(self):
        return self.Sensors.imu.readAccelerometerMaster()
    
    def getGyro(self):
        return self.Sensors.imu.readGyroscopeMaster()

    def getMag(self):
        return self.Sensors.imu.readMagnetometerMaster()
    
    def getPressure(self):
        return self.Sensors.bmp280.pressure
    
    def getTemperature(self):
        return self.Sensors.bmp280.temperature
    
    def getAltitudeBMP280(self):
        return self.Sensors.bmp280.altitude