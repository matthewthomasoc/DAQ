# Dependencies
import board, smbus, serial, configparser
from easydict import EasyDict as edict

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
        self.cfg = configparser.ConfigParser()

        self.cfg.read(path)

    def initSensors(self):
        self.logger.debug("Initializing BMP280")
        self.initBMP280(self.cfg['BMP280'])

        self.logger.debug("Initializing MPU9250")
        self.initMPU9250(self.cfg['MPU9250'])

        #self.logger.debug("Initializing NEO6M")
        #self.initNEO6M(self.cfg['NEO6M'])
    
    def initBMP280(self, cfg):
        try:
            self.Sensors.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(board.I2C())
            self.Sensors.bmp280.sea_level_pressure = cfg['SEALEVEL_PA']
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
        except Exception as ex:
            self.logger.debug("Failure while initializing MPU9250!")
            raise ex

    def initNEO6M(self, cfg):
        port = "/dev/ttyAMA0"
        #self.Sensors.gps = 

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
    
    def sendCommandToGPS(self, cmd):
        self.Sensors.gps.write(serial.to_bytes(cmd))

# class NEO6M():
#     def __init__(self, port):
#         self.serial = serial.Serial(port, baudrate=9600, timeout=0.5)

# Notes
# GPS NMEA sentences
# In-flight (@ 10 Hz):
# GGA (LLA, # Sats, Altitude, HDOP)
# Debug (@ 5 Hz):
# GGA (LLA, # Sats, Altitude, HDOP)
# GSA (2D/3D fix, # sats used for fix, HDOP, VDOP)
# GSV (# sats in view, sat elevations, sat azimuths, sat SNR)

# 0xB5,0x62,0x06,0x08,0x06,0x00,0x64,0x00,0x01,0x00,0x01,0x00,0x7A,0x12, // 10Hz
# 0xB5,0x62,0x06,0x08,0x06,0x00,0xC8,0x00,0x01,0x00,0x01,0x00,0xDE,0x6A, // 5Hz
# 0xB5,0x62,0x06,0x08,0x06,0x00,0xE8,0x03,0x01,0x00,0x01,0x00,0x01,0x39 // 1Hz

# 0xB5,0x62,0x06,0x01,0x08,0x00,0xF0,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x24, // GxGGA off
# 0xB5,0x62,0x06,0x01,0x08,0x00,0xF0,0x01,0x00,0x00,0x00,0x00,0x00,0x01,0x01,0x2B, // GxGLL off
# 0xB5,0x62,0x06,0x01,0x08,0x00,0xF0,0x02,0x00,0x00,0x00,0x00,0x00,0x01,0x02,0x32, // GxGSA off
# 0xB5,0x62,0x06,0x01,0x08,0x00,0xF0,0x03,0x00,0x00,0x00,0x00,0x00,0x01,0x03,0x39, // GxGSV off
# 0xB5,0x62,0x06,0x01,0x08,0x00,0xF0,0x04,0x00,0x00,0x00,0x00,0x00,0x01,0x04,0x40, // GxRMC off
# 0xB5,0x62,0x06,0x01,0x08,0x00,0xF0,0x05,0x00,0x00,0x00,0x00,0x00,0x01,0x05,0x47, // GxVTG off