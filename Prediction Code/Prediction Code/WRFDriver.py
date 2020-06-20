import WRFPrediction
import Calculations
import numpy as np

start_lat = 46.83982 #decimal degrees (46.8601 for UM Oval)
start_lon = -114.05418 #decimal degrees (-113.9852 for UM Oval)
start_alt = 978.0 #m
max_alt = 24000.0 #m
#WRF FILE AND DIRECTORY
wrf_file = 'wrfout_d02_2015-07-29_19:00:00' #UTC hour required
main_directory = '/home/jaylene/Documents/WRF/WRFV3/test/em_real/'

#Predictions
points = WRFPrediction.Prediction(wrf_file, main_directory, start_lat, start_lon, start_alt, max_alt)

#Plotting
Calculations.Plotting(points, 400000, 400000)

#Write file
np.savetxt('WRFtest.txt', points, fmt='%9.8f', delimiter='\t', header='Latitude\tLongitude\tAltitude(m)\tRise Rate(m/s)')
