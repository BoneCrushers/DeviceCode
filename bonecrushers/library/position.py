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

class Positioner:

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
        
