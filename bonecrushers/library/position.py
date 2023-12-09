# Simple positioning library using MPU6050 accelerometer connected via I2C.
# A lot of this is based on: https://github.com/ElectronicCats/mpu6050

# You can use a CH341-based adapter like this one: 
#    https://www.amazon.com/DSD-TECH-SH-U05A-UART-Adatper/dp/B0BM9JQZB7

# The accelerometer/gyro board is this one:
#    https://www.amazon.com/Gy-521-MPU-6050-MPU6050-Sensors-Accelerometer/dp/B008BOPN40

# Simply connect VCC, GND, SCL and SDA between the USB interface and the MPU6050.

# I2C address for the position sensor is 0x68.
# Detect device by probing data address 0x75 - should return 0x68.

import smbus2
import struct

REG_GYRO_CONFIG = 0x1b
REG_ACCEL_CONFIG = 0x1c
REG_PWR_MGMT_1 = 0x6b

REG_ACCEL = 0x3b
REG_TEMP = 0x41
REG_GYRO = 0x43

class Positioner:

    def _read(self,addr):
        return self.BUS.read_byte_data(self.ADDR,addr)
    def _write(self,addr,value):
        self.BUS.write_byte_data(self.ADDR,addr,value)
    def _readmany(self,addr,count):
        return self.BUS.read_i2c_block_data(self.ADDR,addr,count)

    @property
    def accel(self):
        """Returns current raw accelerometer readings as [x,y,z]"""
        raw = bytes(self._readmany(REG_ACCEL,6))
        return struct.unpack(">hhh",raw)

    @property
    def gyro(self):
        """Returns current raw gyroscope readings as [x,y,z]"""
        raw = bytes(self._readmany(REG_GYRO,6))
        return struct.unpack(">hhh",raw)

    @property
    def temp(self):
        """Returns current raw temperature value"""
        raw = bytes(self._readmany(REG_TEMP,2))
        return struct.unpack(">h",raw)[0]
    
    @property
    def temp_c(self):
        """Returns current temperature converted to degrees Celsius"""
        return self.temp / 340 + 36.53
    
    @property
    def readings(self):
        """Returns all sensor readings in one shot as a dictionary containing "accel", "gyro" and "temp"."""
        raw = bytes(self._readmany(REG_ACCEL,12))
        data = struct.unpack(">hhhhhhh",raw)
        return {
            "accel": (data[0],data[1],data[2]),
            "gyro": (data[4],data[5],data[6]),
            "temp": data[3]
        }
    
    def available(self):

        # try to read from address 0x75 of device
        try:
            b = self.BUS.read_byte_data(self.ADDR,0x75)
            if b != 0x68: return False
            return True
        except:
            return False # something went wrong, we don't really care what.

    def __init__(self, i2c_bus=10, i2c_addr=0x68):

        self.BUS = smbus2.SMBus(i2c_bus)
        self.ADDR = i2c_addr

        # test if device is available
        if not self.available():
            raise RuntimeError("I2C device not available.")
        
        # set clock source to XGyro
        self._write(REG_PWR_MGMT_1,0b01000001)

        # set gyro range to 250
        self._write(REG_GYRO_CONFIG,0b00000000)

        # set accelerometer range to 2g
        self._write(REG_ACCEL_CONFIG,0b00000000)

        # wake up device
        self._write(REG_PWR_MGMT_1,0b00000001)

