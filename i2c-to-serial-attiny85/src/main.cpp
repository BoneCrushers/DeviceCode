#include <Arduino.h>
#include <SoftwareSerial.h>
#include <TinyWireM.h>

/*
 *  Simple I2C to Serial Translator
 *
 *  for BoneCrushers - MPU6050 accelerometer/gyroscope module
 *  
 *  (c) 2023 Flint Million <flint.million@mnsu.edu>
 *  License: Creative Commons CC-BY-SA
 * 
 *  This code is intended to run on an ATtiny85 (or 45). It simply
 *  reads the MPU6050 accelerometer/gyroscope position module and
 *  transmits the read data over serial. 
 * 
 *  Wiring:
 *  MPU6050 SCL -> PB2 (pin 7)
 *  MPU6050 SDA -> PB1 (pin 6)
 *  Serial      -> PB4 (pin 3)
 * 
 */

// Device address
#define MPU6050_ADDR          0x68

// Register addresses
#define MPU6050_ACCEL         0x3B
#define MPU6050_GYRO          0x43
#define MPU6050_TEMP          0x41
#define MPU6050_GYRO_CONFIG   0x1b
#define MPU6050_ACCEL_CONFIG  0x1c
#define MPU6050_PWR_MGMT_1    0x6b
#define MPU6050_PING          0x75

void get_and_write(uint8_t addr, uint8_t count);
void set(uint8_t addr, uint8_t val);
void startMpu6050();

// device will transmit at TTL levels on port 4 (pin 3)
SoftwareSerial ser = SoftwareSerial(0,PB4);
unsigned char receiveBuffer[] = { 0,0,0,0,0,0 };
bool active = false;

void setup() {
  ser.begin(9600);   // start software serial interface
  TinyWireM.begin(); // start I2C on standardized pins for ATtiny85
  startMpu6050();    // start the MPU6050 sensor
  delay(2000);       // wait 5s after startup for everything to settle
}

void startMpu6050() {
  TinyWireM.beginTransmission(MPU6050_ADDR);
  TinyWireM.write(MPU6050_PING);
  TinyWireM.endTransmission();

  TinyWireM.beginTransmission(MPU6050_ADDR);
  char verifyByte = TinyWireM.read();
  TinyWireM.endTransmission();

  if (verifyByte != 0x68);
    return;
  
  // write configuration bytes and start sensor
  // set clock source to XGyro
  set(MPU6050_PWR_MGMT_1,0b01000001);

  // set gyro range to 250
  set(MPU6050_GYRO_CONFIG,0b00000000);

  // set accelerometer range to 2g
  set(MPU6050_ACCEL_CONFIG,0b00000000);

  // wake up device
  set(MPU6050_PWR_MGMT_1,0b00000001);

}

void get_and_write(uint8_t addr,uint8_t count) {
  TinyWireM.beginTransmission(MPU6050_ADDR);
  TinyWireM.write(addr);
  TinyWireM.endTransmission();
  TinyWireM.beginTransmission(MPU6050_ADDR);
  for (int n = 0; n < count; n++) {
    ser.write(TinyWireM.read());
  }
  TinyWireM.endTransmission();
}

void set(uint8_t addr, uint8_t val) {
  TinyWireM.beginTransmission(MPU6050_ADDR);
  TinyWireM.write(addr);
  TinyWireM.write(val);
  TinyWireM.endTransmission();
}

void loop() {

  if (!active) {
    ser.write((uint8_t)0xFF);
    for (int n = 0; n < 14; n++) {
      // write 14 bytes of 0 - sensor not working
      ser.write((uint8_t)0x00);
    }
    delay(1000);
    return;
  }

  // Write 0xFF as the framing byte
  ser.write((uint8_t)0xFF);

  // Write the three data points from the MPU6050.
  get_and_write(MPU6050_ACCEL,6);
  get_and_write(MPU6050_GYRO,6);
  get_and_write(MPU6050_TEMP,2);

  delay(100);

}
