from bonecrushers.library.position import Positioner
import time

def main():

    try:
        p = Positioner()
        print(f"The test was successful.")
        
        while True:
            print(p.temp_c)
            print(p.accel)
            print(p.gyro)
            time.sleep(1)
            print()

    except RuntimeError as ex:
        print(f"The test was not successful: {ex}")
