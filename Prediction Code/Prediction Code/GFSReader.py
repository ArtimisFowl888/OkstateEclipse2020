#from netCDF4 import Dataset
import nio
import numpy as np
import time
import datetime

#CONSTANTS
DEGREES_TO_RADIANS = np.pi/180.0
RADIANS_TO_DEGREES = 180.0/np.pi

def accessGFS():
    baseURL = 'http://nomads.ncep.noaa.gov:9090/dods/gfs_0p25/'
    GFSDate = int(time.strftime("%Y%m%d"))
    currentHour = time.gmtime()[3]
    #GFS data isn't uploaded until roughly 4.5 hours after the hour of prediction
    gfsTimeHeader = 'gfs_0p25_'
    if currentHour > 22:
        timeURL = gfsTimeHeader + '18z'
        GFSTime = 18
    elif currentHour > 16:
        timeURL = gfsTimeHeader + '12z'
        GFSTime = 12
    elif currentHour > 10:
        timeURL = gfsTimeHeader + '06z'
        GFSTime = 6
    elif currentHour > 4:
        timeURL = gfsTimeHeader + '00z'
        GFSTime = 0
    else:
        timeURL = gfsTimeHeader + '18z'
        GFSTime = 18
        GFSDate -= 1
    GFSDate = str(GFSDate)
    GFSDateTime = datetime.datetime(int(GFSDate[:4]),int(GFSDate[4:6]),int(GFSDate[6:]),GFSTime, 0, 0)
    dateURL = 'gfs' + GFSDate + '/'
    url = baseURL + dateURL + timeURL

    attempts = 0
    while attempts < 3:
        attempts += 1
        try:
            GFS = Dataset(url)
            attempts = 3
            return GFS, GFSDateTime
        except:
            print 'Failure to access GFS server. (attempt: %s)' %attempts

def accessGFSDate(GFSDate):
    baseURL = 'http://nomads.ncep.noaa.gov:9090/dods/gfs_0p25/'
##    GFSDate = int(time.strftime("%Y%m%d"))
    currentHour = GFSDate.hour
    #GFS data isn't uploaded until roughly 4.5 hours after the hour of prediction
    gfsTimeHeader = 'gfs_0p25_'
    if currentHour > 18:
        timeURL = gfsTimeHeader + '18z'
        GFSTime = 18
    elif currentHour > 12:
        timeURL = gfsTimeHeader + '12z'
        GFSTime = 12
    elif currentHour > 6:
        timeURL = gfsTimeHeader + '06z'
        GFSTime = 6
    elif currentHour > 0:
        timeURL = gfsTimeHeader + '00z'
        GFSTime = 0
    else:
        timeURL = gfsTimeHeader + '18z'
        GFSTime = 18
        GFSDate -= 1
    GFSDateTime = GFSDate
    GFSDate = str(GFSDate.date()).replace('-', '')
    dateURL = 'gfs' + GFSDate + '/'
    url = baseURL + dateURL + timeURL

    attempts = 0
    while attempts < 3:
        attempts += 1
        try:
            GFS = Dataset(url)
            attempts = 3
            return GFS, GFSDateTime
        except:
            print 'Failure to access GFS server. (attempt: %s)' %attempts

def accessHistoricGFS(year, month, day, hour):
    GFSYear = str(year)
    GFSMonth = str(month).zfill(2)
    GFSDay = str(day).zfill(2)
    GFSDate = GFSYear + GFSMonth + GFSDay
    baseURL = 'http://nomads.ncdc.noaa.gov/dods/NCEP_GFS/%s/%s/' %(GFSYear + GFSMonth, GFSDate)
    #GFS data isn't uploaded until roughly 4.5 hours after the hour of prediction
    gfsFileHeader = 'gfs_3_%s_' %(GFSDate)
    if hour > 17 and hour < 24:
        timeURL = gfsFileHeader + '1800_fff'
        GFSTime = 18
    elif hour > 11:
        timeURL = gfsFileHeader + '1200_fff'
        GFSTime = 12
    elif hour > 5:
        timeURL = gfsFileHeader + '0600_fff'
        GFSTime = 6
    elif hour >= 0:
        timeURL = gfsFileHeader + '0000_fff'
        GFSTime = 0
    else:
        print 'Incorrect hour entry'
    GFSDateTime = datetime.datetime(int(GFSYear),int(GFSMonth),int(GFSDay),GFSTime, 0, 0)
    url = baseURL + timeURL

    attempts = 0
    while attempts < 3:
        attempts += 1
        try:
            GFS = Dataset(url)
            attempts = 3
            return GFS, GFSDateTime
        except:
            print 'Failure to access GFS server. (attempt: %s)' %attempts


def findGFSTimeIndex(predictionDateTime, GFSDateTime):
    diff = predictionDateTime - GFSDateTime
    #GFS data is incremented every 3 hours
    return int(np.round((diff.total_seconds()/3600)/3))
    

def findGFSLatLonIndex(gfs, lat, lon):
    if lon < 0:
        lon = 360 + lon
    lats = gfs.variables['lat'][:]
    lons = gfs.variables['lon'][:]
    error_lat = 0
    error_lon = 0
    previous_error_lat = 9999
    previous_error_lon = 9999
    index_i=0
    index_j=0
    for j in range(len(lats)):
        error_lat = abs(lat - lats[j])
        if error_lat < previous_error_lat:
            index_j = j
            previous_error_lat = error_lat
    for i in range(len(lons)):
        error_lon = abs(lon - lons[i])
        if error_lon < previous_error_lon:
            index_i = i
            previous_error_lon = error_lon
    return index_i, index_j

def getTerrainHeight(gfs, timeIndex, index_i, index_j):
    return gfs.variables['hgtsfc'][timeIndex, index_j, index_i]

def getGFSAlts(gfs, timeIndex, index_i, index_j):
    #Historic data has hgt current data has hgtprs
    ALT = gfs.variables["hgtprs"][timeIndex,:,index_j,index_i]
    return ALT

##def findGFSAltIndex(gfs, timeIndex, index_i, index_j, alt):
def findGFSAltIndex(gfs, ALT, alt):
##    ALT = gfs.variables["hgtprs"][timeIndex,:,index_j,index_i]
    error = 0
    previous_error = 9999
    index_k = 0
    for k in range(len(ALT)):
        error = abs(alt - ALT[k])
        if  error < previous_error:
            index_k = k
            previous_error = error
    return index_k

def getWindSpeedAndDirection(gfs, timeIndex, index_i, index_j, index_k, web=True, grib1=False):
    if web:
        #Historic data has u/vgrnd while current has u/vugrdprs
        U = gfs.variables["ugrdprs"][timeIndex, index_k, index_j, index_i]
        V = gfs.variables["vgrdprs"][timeIndex, index_k, index_j, index_i]
    else:
        if(grib1):
            U = -gfs.variables['U_GRD_3_ISBL'][index_k, index_j, index_i]
            V = -gfs.variables['V_GRD_3_ISBL'][index_k, index_j, index_i]
        else:
            U = gfs.variables['UGRD_P0_L100_GLL0'][index_k, index_j, index_i]
            V = gfs.variables['VGRD_P0_L100_GLL0'][index_k, index_j, index_i]
    if U > 100:
        U = 0
    if V > 100:
        V = 0
    windDir = RADIANS_TO_DEGREES * np.arctan2(U, V)
    windSpd = np.sqrt(U**2 + V**2)
    return windSpd, windDir
    
def openGFS(main_directory, file_name):
    try:
        gfs = nio.open_file(main_directory + file_name, 'r')
        return gfs
    except:
        print 'Something went wrong'

def findNetCDFLatLonIndex(gfs, lat, lon):
    if lon < 0:
        lon = 360 + lon
    lats = gfs.variables['lat_0'][:]
    lons = gfs.variables['lon_0'][:]
    error_lat = 0
    error_lon = 0
    previous_error_lat = 9999
    previous_error_lon = 9999
    index_i=0
    index_j=0
    for j in range(len(lats)):
        error_lat = abs(lat - lats[j])
        if error_lat < previous_error_lat:
            index_j = j
            previous_error_lat = error_lat
    for i in range(len(lons)):
        error_lon = abs(lon - lons[i])
        if error_lon < previous_error_lon:
            index_i = i
            previous_error_lon = error_lon
    return index_i, index_j

def findNetCDFAltIndex(gfs, index_i, index_j, alt):
    PH = gfs.variables["lv_ISBL0"][:] * .01 #hPa
    ALT = [(1-(PH[i]/1013.25)**0.190284)*145366.45*.3048 for i in range(len(PH)-1)] #m
    error = 0
    previous_error = 9999
    index_k = 0
    for k in range(len(ALT)):
        error = abs(alt - ALT[k])
        if  error < previous_error:
            index_k = k
            previous_error = error
    return index_k

def findGribLatLonIndex(gfs, lat, lon):
    lats = gfs.variables['lat_3'][:]
    lons = gfs.variables['lon_3'][:]
    error_lat = 0
    error_lon = 0
    previous_error_lat = 9999
    previous_error_lon = 9999
    index_i=0
    index_j=0
    for j in range(len(lats)):
        error_lat = abs(lat - lats[j])
        if error_lat < previous_error_lat:
            index_j = j
            previous_error_lat = error_lat
    for i in range(len(lons)):
        error_lon = abs(lon - lons[i])
        if error_lon < previous_error_lon:
            index_i = i
            previous_error_lon = error_lon
    return index_i, index_j

def findGribAltIndex(gfs, index_i, index_j, alt):
    PH = gfs.variables["lv_ISBL3"][:] #hPa
    ALT = [(1-(PH[i]/1013.25)**0.190284)*145366.45*.3048 for i in range(len(PH)-1)] #m
    error = 0
    previous_error = 9999
    index_k = 0
    for k in range(len(ALT)):
        error = abs(alt - ALT[k])
        if  error < previous_error:
            index_k = k
            previous_error = error
    return index_k
