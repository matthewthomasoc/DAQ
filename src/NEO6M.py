import serial, configparser

class NEO6M():
    def __init__(self, cfg, logger):
        # Save attributes
        self.cfg = cfg
        self.logger = logger
        
        # Initialize serial communication GPS port
        self.serial = serial.Serial(self.cfg['PORT'], baudrate=int(self.cfg['BAUDRATE']), timeout=0.5)
        self.logger.debug("Started serial connection on port " + self.cfg['PORT'] + " with baudrate of " + self.cfg['BAUDRATE'])

        # Parse GPS commands config file
        self.cmds = configparser.ConfigParser()
        self.cmds.read(cfg['CMD_CONFIG'])

        self.parseConfig()

    def parseConfig(self):
        # Set NMEA sentence enable/disable from config,
        disabledNMEA = ""
        cmd = list()
        if self.cfg.getboolean('DISABLE_GGA'):
            cmd += eval(self.cmds['GPS_NMEA_CMDS']['DISABLE_GGA'])
            disabledNMEA += "GGA, "
        if self.cfg.getboolean('DISABLE_GLL'):
            cmd += eval(self.cmds['GPS_NMEA_CMDS']['DISABLE_GLL'])
            disabledNMEA += "GLL, "
        if self.cfg.getboolean('DISABLE_GSA'):
            cmd += eval(self.cmds['GPS_NMEA_CMDS']['DISABLE_GSA'])
            disabledNMEA += "GSA, "
        if self.cfg.getboolean('DISABLE_GSV'):
            cmd += eval(self.cmds['GPS_NMEA_CMDS']['DISABLE_GSV'])
            disabledNMEA += "GSV, "
        if self.cfg.getboolean('DISABLE_RMC'):
            cmd += eval(self.cmds['GPS_NMEA_CMDS']['DISABLE_RMC'])
            disabledNMEA += "RMC, "
        if self.cfg.getboolean('DISABLE_VTG'):
            cmd += eval(self.cmds['GPS_NMEA_CMDS']['DISABLE_VTG'])
            disabledNMEA += "VTG"
        self.logger.debug("Disabled NMEA messages: " + disabledNMEA)

        # Set refresh rate from config,
        if self.cfg['REFRESH_RATE'] == '10': # 10 Hz
            cmd += eval(self.cmds['GPS_RATE_CMDS']['SET_10HZ'])
            self.logger.debug("Set GPS refresh rate to 10 Hz")
        elif self.cfg['REFRESH_RATE'] == '5': # 5 Hz
            cmd += eval(self.cmds['GPS_RATE_CMDS']['SET_5HZ'])
            self.logger.debug("Set GPS refresh rate to 5 Hz")
        elif self.cfg['REFRESH_RATE'] == '1': # 1 Hz
            cmd += eval(self.cmds['GPS_RATE_CMDS']['SET_1HZ'])
            self.logger.debug("Set GPS refresh rate to 1 Hz")
        else:
            cmd += eval(self.cmds['GPS_RATE_CMDS']['SET_1HZ'])
            self.logger.debug("No refresh rate specified in config. Set GPS refresh rate to 1 Hz")
        
        self.sendCommand(cmd)
    
    def sendCommand(self, cmd):
        self.serial.write(serial.to_bytes(cmd))

# Notes
# GPS NMEA sentences
# In-flight (@ 10 Hz):
# GGA (LLA, # Sats, Altitude, HDOP)
# Debug (@ 5 Hz):
# GGA (LLA, # Sats, Altitude, HDOP)
# GSA (2D/3D fix, # sats used for fix, HDOP, VDOP)
# GSV (# sats in view, sat elevations, sat azimuths, sat SNR)