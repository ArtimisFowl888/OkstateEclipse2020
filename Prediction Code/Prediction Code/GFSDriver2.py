import GFSReader
import Calculations
import numpy as np

#USER INITIAL VARIABLES
start_lat = 44.16850716 #decimal degrees (46.8601 for UM Oval)
start_lon = -112.21991301 #decimal degrees (-113.9852 for UM Oval)
start_alt = 1418 #m
max_alt = 30000.0 #m
#WRF FILE AND DIRECTORY
gfs_file = 'fnl_20160821_12_00.grib2' #UTC hour required
main_directory = '~/Downloads/'
ascent_only = False

radius_parachute = 0.28 #m (0.28 m for GRAW red parachute) 
#Balloon Info: http://kaymontballoons.com/Weather_Forecasting.html
radius_balloon = 1.8 #m (200g balloon has radius of 1.95 ft = 0.59436 m)
mass_balloon = 2000 #g
mass_payload = 5400 #g

#Floating balloon variables for testing
floating_balloon = False
duration = 0
time_in_float = 0
floating = False
TIME_INCREMENT = 0
#NONUSER VARIABLES
ascent = True
done = False
points = []
#arbitraty initial rise rate
rise_rate = 5.0
hour_duration = 0
terrain_height = start_alt
current_lat = start_lat
current_lon = start_lon
current_alt = start_alt
latLonAlt = [current_lat, current_lon, current_alt, rise_rate]
points.append(latLonAlt)

grib1 = False
if(gfs_file[-5:] == 'grib1'):
    grib1 = True

#CONSTANTS
ALT_INCREMENT = 50.0 #m
#PREDICTION PROCESS
gfs = GFSReader.openGFS(main_directory, gfs_file)
while(not done):
    if(grib1):
        x,y = GFSReader.findGribLatLonIndex(gfs,current_lat,current_lon)
        z = GFSReader.findGribAltIndex(gfs,x,y,current_alt-start_alt)
    else:
        x,y = GFSReader.findNetCDFLatLonIndex(gfs,current_lat,current_lon)
        z = GFSReader.findNetCDFAltIndex(gfs,x,y,current_alt-start_alt)

    w_spd, w_dir = GFSReader.getWindSpeedAndDirection(gfs,0,x,y,z, False, grib1)
    
    if not floating:
        rise_time = 1/abs(rise_rate) * ALT_INCREMENT
        distance = rise_time * w_spd
    else:
        rise_time = TIME_INCREMENT
        distance = rise_time * w_spd

##    hour_duration += rise_time
##    if hour_duration >= 10800:
##        old_gfs = gfs_file
##        gfs_time = int(gfs_file[22:25]) + 3
##        gfs_file =  gfs_file[:22] + str(gfs_time).zfill(3) + gfs_file[25:]
##        gfs = GFSReader.openGFS(main_directory, gfs_file)
##        hour_duration = 0
    
    current_lat, current_lon = Calculations.destination(distance/1000, w_dir, current_lat, current_lon)

    if(ascent):
        current_alt += ALT_INCREMENT
##        rise_rate = Calculations.getAscentRate(wrf,x,y,z,radius_balloon,float(mass_balloon)/1000.0,float(mass_payload)/1000.0)
        rise_rate = Calculations.getRiseRate(current_alt, ascent)
##        rise_rate = Calculations.getRiseRateTest(current_alt, ascent)
        if(current_alt >= max_alt):
            print 'burst'
            ascent = False
    else:
        if(ascent_only):
            break
        if(floating_balloon and time_in_float < duration):
            time_in_float+=TIME_INCREMENT
            floating = True
        else:
            floating = False
            current_alt -= ALT_INCREMENT
##            rise_rate = Calculations.getDecentRate(wrf,x,y,z,float(radius_parachute),float(mass_balloon)/1000,float(mass_payload)/1000)
            rise_rate = Calculations.getRiseRate(current_alt, ascent)
##            rise_rate = Calculations.getRiseRateTest(current_alt, ascent)
            if(current_alt <= terrain_height):
                done = True
                current_alt = terrain_height
    latLonAlt = [current_lat, current_lon, current_alt, rise_rate]
    points.append(latLonAlt)
gfs.close()
#Plotting
##Calculations.Plotting(points, 400000, 400000)

np.savetxt('GFStest.txt', points, fmt='%9.8f', delimiter='\t', header='Latitude\tLongitude\tAltitude\tRise Rate')

