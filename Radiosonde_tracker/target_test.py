import board
import numpy as np
import time
import busio
from adafruit_servokit import ServoKit
import adafruit_pca9685
import adafruit_lsm9ds1
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as ureq

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
# servo set up
pca = adafruit_pca9685.PCA9685(i2c, 0x41)
kit = ServoKit(channels=16)
pca.frequency = 50
kit.servo[0].actuation_range = 140
kit.servo[1].actuation_range = 140
# mag setup
mag = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)

# auto_rx scraping set up
url = 'file:///D:/Downloads/Radiosonde%20Auto-RX%20Status.html'

# basic setup
AZt = 0
pi = np.pi
radius = 6371
h = 70
e = 0
el0 = e
kit.servo[0].angle = h
kit.servo[0].angle = e

# ground station gps input
# todo get ground station gps data
use_mag = False
if not use_mag:
    AZz = float(input('What is the Current bearing'))
Lon0 = float(input('What is the Current longitude'))
Lat0 = float(input('What is the Current latitude'))
Alt0 = float(input('What is the Current altitude'))
lor0 = Lon0*(pi/180)
lar0 = Lat0*(pi/180)

while True:
    # mag data
    if use_mag:
        mag_x, mag_y, mag_z = mag.magnetic
        AZz = np.atan2(mag_y, mag_x)*(180/pi)
        if AZz < 0:
            AZz = AZz+360
    # radiosonde data from auto_rx
    uclient = ureq(url)
    page_raw = uclient.read()
    uclient.close()
    page = soup(page_raw, "html.parser")
    html_lat = page.findAll("div", {"tabulator-field": "lat"})
    html_lon = page.findAll("div", {"tabulator-field": "lon"})
    html_alt = page.findAll("div", {"tabulator-field": "alt"})
    lat = html_lat[1].text
    lon = html_lon[1].text
    alt = html_alt[1].text
    Lont = float(lon)
    Latt = float(lat)
    Altt = float(alt)
    lort = Lont*(pi/180)
    lart = Latt*(pi/180)
    # calculate Azimuth
    dlo = lort-lor0
    dla = lart-lar0
    az = np.atan2(np.sin(dlo)*np.cos(lart), np.cos(lar0)*np.sin(lart)-np.sin(lar0)*np.cos(lart)*np.cos(dlo))
    az = az*(180/pi)
    if az < 0:
        AZt = az+360

    # calculate elevation
    x = dlo*np.cos((lar0+lart)/2)
    y = dla
    rkm = radius*np.sqrt(x*x+y*y)
    dalt = Alt0-Altt
    j = dalt/(rkm*1000)
    elv = np.atan(j)
    elv = elv*(180/pi)

    # rotate to match bearing
    if AZz > AZt:
        dh = AZz-AZt
        h = h-dh
        if h < 5:
            h = 0
        kit.servo[0].angle = h
    elif AZz == AZt:
        h = h
        kit.servo[0].angle = h
    else:
        dh = AZt-AZz
        h = h+dh
        if h > 135:
            h = 140
        kit.servo[0].angle = h
    # rotate to match elevation
    if elv > el0:
        de = el0-elv
        e = e+de
        if e > 85:
            e = 85
        kit.servo[1].angle = e
    elif elv == el0:
        e = e
        kit.servo[1].angle = e
    else:
        de = el0-elv
        e = e-de
        if e < 5:
            e = 5
        kit.servo[1].angle = e
    AZz = h
    el0 = e
    time.sleep(5)
