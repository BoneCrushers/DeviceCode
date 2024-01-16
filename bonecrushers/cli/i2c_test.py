from bonecrushers.library import ch341
import time

def printhex(d):
    for s in range(0,len(d),8):

        if s % 16 == 0:
            print(hex(s)[2:].zfill(8) + "    ",end='')

        print(" ".join([hex(x)[2:].zfill(2).upper() for x in d[s:s+8]]),end='')
        if s % 16 == 8:
            print()
        else:
            print("   ",end='')

def main():

    try:
        bus = ch341.CH341()
    except ConnectionError:
        print("No I2C USB adapter found.")
        return

    bytelen=128
    for _ in range(10):

        d = []
        for y in range(0,bytelen,32):
            d += list(bus.read_i2c_block_data(0x68,y,32))
            bus.read_i2c_block_data(0x68,y,32) # discard extra read
        printhex(d)
        print()
        time.sleep(1)
