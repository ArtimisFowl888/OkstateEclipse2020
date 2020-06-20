import GFSReader
import Calculations
import datetime
import numpy as np

#USER INITIAL VARIABLES
flight_hour = 18 #UTC hour
flight_day = 5
flight_month = 12
flight_year = 2016
flightDate = datetime.datetime(flight_year, flight_month, flight_day, flight_hour, 0, 0)

radius_parachute = 0.28 #m (0.28 m for GRAW red parachute) 
#Balloon Info: http://kaymontballoons.com/Weather_Forecasting.html
radius_balloon = 0.59436 #m (200g balloon has radius of 1.95 ft = 0.59436 m)
mass_balloon = 200 #g
mass_payload = 140 #g
start_lat = 46.8601 #decimal degrees (46.8601 for UM Oval)
start_lon = -113.9852 #decimal degrees (-113.9852 for UM Oval)
start_alt = 978.0 #m (1470 for UM Oval)
max_alt = 25000.0 #m

#Floating balloon variables for testing
floating_balloon = False
duration = 3600
time_in_float = 0
floating = False
TIME_INCREMENT = 30
#NONUSER VARIABLES
ascent = True
done = False
points = []
#arbitraty initial rise rate
rise_rate = 5.0
current_lat = start_lat
current_lon = start_lon
current_alt = start_alt
latLonAlt = [current_lat, current_lon, current_alt, rise_rate]
points.append(latLonAlt)

#CONSTANTS
ALT_INCREMENT = 150.0 #m
#PREDICTION PROCESS
gfs, gfsDate = GFSReader.accessGFS()
##gfs, gfsDate = GFSReader.accessHistoricGFS(flight_year, flight_month, flight_day, flight_hour)
timeIndex = GFSReader.findGFSTimeIndex(flightDate, gfsDate)
x,y = GFSReader.findGFSLatLonIndex(gfs, current_lat, current_lon)
terrain_height = 850. #GFSReader.getTerrainHeight(gfs,timeIndex,x,y)
alts = GFSReader.getGFSAlts(gfs,timeIndex,x,y)
while(not done):
    z = GFSReader.findGFSAltIndex(gfs,alts,current_alt)
    w_spd, w_dir = GFSReader.getWindSpeedAndDirection(gfs,timeIndex,x,y,z)

    if not floating:
        rise_time = 1/abs(rise_rate) * ALT_INCREMENT
        distance = rise_time * w_spd
    else:
        rise_time = TIME_INCREMENT
        distance = rise_time * w_spd

##    hour_duration += rise_time
##    if hour_duration >= 3600:
##        wrf_time = int(wrf_file[22:24]) + 1
##        wrf_file =  wrf_file[:22] + str(wrf_time) + wrf_file[24:]
##        wrf = WRFReader.openWRF(main_directory, wrf_file)
##        hour_duration = 0
    
    current_lat, current_lon = Calculations.destination(distance/1000, w_dir, current_lat, current_lon)

    if(ascent):
        current_alt += ALT_INCREMENT
        rise_rate = Calculations.getRiseRate(current_alt, ascent)
        if(current_alt >= max_alt):
            print 'burst'
            ascent = False
    else:
        if(floating_balloon and time_in_float < duration):
            time_in_float+=TIME_INCREMENT
            floating = True
        else:
            floating = False
            current_alt -= ALT_INCREMENT
            rise_rate = Calculations.getRiseRate(current_alt, ascent)
            if(current_alt <= terrain_height):
                done = True
                current_alt = terrain_height
    latLonAlt = [current_lat, current_lon, current_alt, rise_rate]
    points.append(latLonAlt)
gfs.close()
#Plotting
Calculations.Plotting(points, 400000, 400000)

np.savetxt('GFStest.txt', points, fmt='%9.8f', delimiter='\t', header='Latitude\tLongitude\tAltitude\tRise Rate')
