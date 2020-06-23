import board
import numpy as np
import time
import busio
from adafruit_servokit import ServoKit
import adafruit_pca9685
import adafruit_lsm9ds1
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c,0x41)
mag = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
kit = ServoKit(channels=16)
pca.frequency = 50
kit.servo[0].actuation_range = 140
kit.servo[1].actuation_range = 140

pi = np.pi
radius = 6371
h = 70

kit.servo[0].angle = h
Lon0 = float(input('What is the Current longitude'))
Lat0 = float(input('What is the Current latitude'))
Alt0 = float(input('What is the Current altitude'))
lor0 = Lon0*(pi/180)
lar0 = Lat0*(pi/180)

var = 0
while True:
    mag_x, mag_y, mag_z = mag.magnetic
    AZz = np.atan2(mag_y,mag_x)*(180/pi)
    if AZz < 0:
        AZz = AZz+360
    Lont = float(input('What is the target longitude'))
    Latt = float(input('What is the target latitude'))
    Altt = float(input('What is the target altitude'))
    lort = Lont*(pi/180)
    lart = Latt*(pi/180)
    dlo = lort-lor0
    dla = lart-lar0
    az = np.atan2(np.sin(dlo)*np.cos(lart),np.cos(lar0)*np.sin(lart)-np.sin(lar0)*np.cos(lart)*np.cos(dlo))
    az = az*(180/pi)
    if az < 0:
        AZt = az+360
    x = dlo*np.cos((lar0+lart)/2)
    y = dla
    rkm = radius*sqrt(x*x+y*y)
    dalt = Alt0-Altt
    j = dalt/(rkm*1000)
    elv = np.atan(j)
    elv = elv*(180/pi)
    if AZz > AZt:
        dh = AZz-AZt
        h = h-dh
        if h<5:
            h=0
        kit.servo[0].angle = h
    elif AZz == AZt:
        h = h
        kit.servo[0].angle = h
    else:
        dh = AZt-AZz
        h = h+dh
        if h>135:
            h=140
        kit.servo[0].angle = h
    var = var+1
    time.sleep(5)


