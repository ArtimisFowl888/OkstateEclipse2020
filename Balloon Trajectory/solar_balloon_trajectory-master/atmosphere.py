# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pygrib
import numpy as np
import os
import urllib
from datetime import datetime
import math
from scipy.interpolate import Rbf, LinearNDInterpolator

from constants import *


class atmosphere:
    default_variables = ["TMP", "UGRD", "VGRD", "HGT", "RH"]
    default_levels = [1000,  975,  950,  925,  900, 850,  800,  750,  700,
                    650,  600, 550, 500, 450, 400, 350, 300, 250, 200, 150,
                    100, 70, 50, 30, 20, 10, 7, 5, 3, 2, 1, "surface"]

    def __init__(self, file_name = "file.anl"):
        grib_file = file_name
        grbs = pygrib.open(grib_file)

        self.lat_ar, self.lon_ar = grbs[1].latlons()
        self.lat_min = np.min(self.lat_ar)
        self.lat_max = np.max(self.lat_ar)
        self.lon_min = np.min(self.lon_ar)
        self.lon_max = np.max(self.lon_ar)
        self.res = self.lat_ar[1,0] - self.lat_ar[0,0]


        self.n_lon = len(self.lon_ar[0])
        self.n_lat = len(self.lat_ar)

        self.levels = []
        for g in grbs:
            level = g.level
            if (not level in self.levels):
                self.levels.append(level)

        self.levels = self.levels[:-1]
        self.n_levels = len(self.levels)

        self.u_ar = np.zeros((self.n_lat, self.n_lon, self.n_levels))
        self.v_ar = np.zeros((self.n_lat, self.n_lon, self.n_levels))
        self.T_ar = np.zeros((self.n_lat, self.n_lon, self.n_levels))
        self.h_ar = np.zeros((self.n_lat, self.n_lon, self.n_levels))
        self.RH_ar = np.zeros((self.n_lat, self.n_lon, self.n_levels))
        self.g_ar = np.zeros((self.n_lat, self.n_lon))

        grbs.seek(0)
        for g in grbs:
            data = g.values
            v = g.shortName
            l = g.level
            li = np.searchsorted(self.levels, l)
            if(v == "u"):
                self.u_ar[:,:,li] = data
            elif (v == "v"):
                self.v_ar[:,:,li] = data
            elif (v == "t"):
                self.T_ar[:,:,li] = data
            elif (v == "gh"):
                self.h_ar[:,:,li] = data
            elif (v == "r"):
                self.RH_ar[:,:,li] = data
            elif(v == "orog"):
                self.g_ar[:,:] = data

        #reverse array order in final index so last index increases with height
        self.u_ar = self.u_ar[:,:,::-1]
        self.v_ar = self.v_ar[:,:,::-1]
        self.T_ar = self.T_ar[:,:,::-1]
        self.h_ar = self.h_ar[:,:,::-1]
        self.RH_ar = self.RH_ar[:,:,::-1]
        self.levels = self.levels[::-1]


        #these are later defined as interpolation functions
        self.P_interp = 0
        self.u_interp = 0
        self.v_interp = 0
        self.T_interp = 0
        self.RH_interp = 0
        self.orog_interp = 0

        #most recent i,j,k bins, used to avoid recomputing interpolation functions
        self.i_cur = -1
        self.j_cur = -1
        self.k_cur = -1

    @staticmethod
    def download_file(lat_range, lon_range, date_hr, file_name,
                      variables = default_variables, levels = default_levels):
        hr = date_hr[-2:]
        header_str = "http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p%s.pl?file=gfs.t%sz.pgrb2.1p00.anl&" %(hr,hr)

        level_str = ""
        for l in levels:
            if(isinstance(l, int)):
                level_str += "lev_%d_mb=on&" % l
            elif(l == "surface"):
                level_str += "lev_%s=on&" % str(l)

        var_str = ""
        for v in variables:
            var_str += "var_%s=on&" % v


        latlon_str = "&subregion=&leftlon=%d&rightlon=%d&toplat=%d&bottomlat=%d&" % (lon_range[0], lon_range[1], lat_range[1], lat_range[0])
        tail_str = "dir=%2Fgfs."
        tail_str += date_hr


        URL = header_str + level_str + var_str + latlon_str + tail_str
        dfile = urllib.URLopener()
        cwd = os.getcwd()

        dfile.retrieve(URL, os.path.join(cwd,file_name))


    def get_bin(self, lat, lon, z, twod = False):
        """"get i, j, k bins in data arrays for position (lat,lon,z)"""
        if(lat < self.lat_min or lat > self.lat_max):
            raise Exception("Bin error: lat %f is outside of lat_ar values (%f %f)" % (lat, self.lat_min, self.lat_max))

        if(lon < self.lon_min or lon > self.lon_max):
            raise Exception("Bin error:lon %f is outside of lon_ar values (%f %f)" % (lon, self.lon_min, self.lon_max))

        i = int((lat - self.lat_min)/self.res)
        j = int((lon - self.lon_min)/self.res)
        if(twod):
            return (i,j,0)
        k = np.searchsorted(self.h_ar[i,j], z, side = 'right')-1
        if(z < self.h_ar[i,j,0]):
            k = 0
        elif(z > self.h_ar[i,j,-1]):
            k = len(self.h_ar[i,j])-1
        return (i,j,k)


    def get_P_interp(self, i, j, k):
        """"
        return a function that uses exponential interpolation to predict pressure value near grid point (i,j,k)

        Parameters:
        i (int): nearest i grid point in lattitude array (self.lat_ar)
        j (int): nearest j grid point in longitude_array (self.lon_ar)
        k (int): nearest k grid point in height_array    (self.h_ar)

        Returns:
        interpolation function which takes (lat,lon,z) and returns interpolated pressure
        """
        loc_lat = []
        loc_lon =  []
        loc_h =  []
        loc_data =  []

        shift = np.zeros(3, dtype=int)

        if(i == self.n_lat -1): shift[0] = -1
        if(j == self.n_lon -1): shift[1] = -1

        if(k == 0):
            shift[2] = 1
        if(k+2 == self.n_levels - 1):
            shift[2] = -1
        if(k+1 == self.n_levels - 1):
            shift[2] = -2
        if(k == self.n_levels - 1):
            shift[2] = -3

        i_range = np.array(range(0,2) + shift[0])
        j_range = np.array(range(0,2) + shift[1])
        k_range = np.array(range(-1,3) + shift[2])

        print(k, k+k_range, shift[2], self.n_levels-1)
        #use a 2x2x2 stencil
        for ii in i_range:
            for jj in j_range:
                for kk in k_range:
                    loc_lat.append(self.lat_ar[i + ii, j + jj])
                    loc_lon.append(self.lon_ar[i + ii, j + jj])
                    loc_h.append(self.h_ar[i+ii, j +jj, k+kk])
                    loc_data.append(self.levels[k+kk])

        points = np.array(list(zip(loc_lat, loc_lon, loc_h)))
        interp = LinearNDInterpolator(points, np.log(loc_data))

        def get_interp(x,y,z):
            return np.exp((interp(x, y, z)))*100 #100 converts m

        return get_interp


    def get_var_interp(self, i, j, k, data_ar):
        """"
        return a function that uses RBF to predict data value at (lat, lon, z) with near grid point (i,j,k)

        Parameters:
        i (int): nearest i grid point in lattitude array (self.lat_ar)
        j (int): nearest j grid point in longitude_array (self.lon_ar)
        k (int): nearest k grid point in height_array    (self.h_ar)

        Returns:
        interpolation function which takes (lat,lon,z) and returns interpolated data value
        """
        loc_lat = []
        loc_lon =  []
        loc_h =  []
        loc_data =  []


        shift = np.zeros(3, dtype=int)

        #use a 3x3 stencil, and shift stencil if i,j,k lie on grid edge
        if(i == 0): shift[0] = 1
        if(j == 0): shift[1] = 1
        if(k == 0): shift[2] = 1

        if(i == self.n_lat -1): shift[0] = -1
        if(j == self.n_lon -1): shift[1] = -1
        if(k == self.n_levels - 1): shift[2] = -1

        i_range = range(-1,2) + shift[0]
        j_range = range(-1,2) + shift[1]
        k_range = range(-1,2) + shift[2]

        for ii in i_range:
            for jj in j_range:
                for kk in k_range:
                    loc_lat.append(self.lat_ar[i + ii, j + jj])
                    loc_lon.append(self.lon_ar[i + ii, j + jj])
                    loc_h.append(self.h_ar[i+ii, j +jj, k+kk])
                    loc_data.append(data_ar[i+ii, j +jj, k+kk])

        #normalize h for better rbf interpolation
        h_scale = (np.max(loc_h) - np.min(loc_h))
        loc_h /= h_scale

        #normalize data for better rbf interpolation
        d_min = np.min(loc_data)
        loc_data -= d_min

        rbfi = Rbf(loc_lat, loc_lon, loc_h, loc_data)
        def  get_interp(rlat, rlon, rh):
            return rbfi(rlat, rlon, rh/h_scale)+d_min

        return get_interp


    def get_orog_interp(self, i, j, data_ar):
        """"
        return a function that uses linear interpolation to predict ground height near grid point (i,j,k)

        Parameters:
        i (int): nearest i grid point in lattitude array (self.lat_ar)
        j (int): nearest j grid point in longitude_array (self.lon_ar)

        Returns:
        interpolation function which takes (lat,lon) and returns interpolated ground height
        """

        loc_lat = []
        loc_lon =  []
        loc_data =  []


        shift = np.zeros(2, dtype=int)

        if(i == self.n_lat -1): shift[0] = -1
        if(j == self.n_lon -1): shift[1] = -1



        i_range = range(0,2) + shift[0]
        j_range = range(0,2) + shift[1]

        #use a 2x2x2 stencil
        for ii in i_range:
            for jj in j_range:
                loc_lat.append(self.lat_ar[i + ii, j + jj])
                loc_lon.append(self.lon_ar[i + ii, j + jj])
                loc_data.append(data_ar[i+ii, j +jj])

        print(loc_lat)
        print(loc_lon)


        points = np.array(list(zip(loc_lat, loc_lon)))

        interp = LinearNDInterpolator(points, loc_data)
        def get_interp(x,y):
            return float(interp(x, y))

        return get_interp



    def get_P(self, lat, lon, z):
        """return interpolated pressure (Pa) at lat(deg), lon(deg), z(m)"""
        #if (i,j,k) bin has changed or interpolation function has not been initialize, recompute interpolation function
        (i,j,k) = self.get_bin(lat,lon,z)
        if ( (i == self.i_cur) and (j == self.j_cur) and (k == self.k_cur) and (self.P_interp != 0)):
            return self.P_interp(lat,lon,z)
        else:
            (self.i_cur, self.j_cur, self.k_cur) = (i, j, k)
            self.P_interp = self.get_P_interp(i, j, k)
            return self.P_interp(lat,lon,z)

    def get_u(self, lat, lon, z):
        """return interpolated u velocity (m/s) at lat(deg), lon(deg), z(m)"""
        #if (i,j,k) bin has changed or interpolation function has not been initialized, recompute interpolation function
        (i,j,k) = self.get_bin(lat,lon,z)
        if ( (i == self.i_cur) and (j == self.j_cur) and (k == self.k_cur) and (self.u_interp != 0)):
            return self.u_interp(lat,lon,z)
        else:
            (self.i_cur, self.j_cur, self.k_cur) = (i, j, k)
            self.u_interp = self.get_var_interp(i, j, k, self.u_ar)
            return self.u_interp(lat,lon,z)

    def get_v(self, lat, lon, z):
        """return interpolated v velocity (m/s) at lat(deg), lon(deg), z(m)"""
        #if (i,j,k) bin has changed or interpolation function has not been initialized, recompute interpolation function
        (i,j,k) = self.get_bin(lat,lon,z)
        if ( (i == self.i_cur) and (j == self.j_cur) and (k == self.k_cur)) and (self.v_interp != 0):
            return self.v_interp(lat,lon,z)
        else:
            (self.i_cur, self.j_cur, self.k_cur) = (i, j, k)
            self.v_interp = self.get_var_interp(i, j, k, self.v_ar)
            return self.v_interp(lat,lon,z)

    def get_T(self, lat, lon, z):
        """return interpolated Temperature (K) at lat(deg), lon(deg), z(m)"""
        #if (i,j,k) bin has changed or interpolation function has not been initialized, recompute interpolation function
        (i,j,k) = self.get_bin(lat,lon,z)
        if ( (i == self.i_cur) and (j == self.j_cur) and (k == self.k_cur) and (self.T_interp != 0)):
            return self.T_interp(lat,lon,z)
        else:
            (self.i_cur, self.j_cur, self.k_cur) = (i, j, k)
            self.T_interp = self.get_var_interp(i, j, k, self.T_ar)
            return self.T_interp(lat,lon,z)

    def get_RH(self, lat, lon, z):
        """return interpolated relative humidity (%) at lat(deg), lon(deg), z(m)"""
        #if (i,j,k) bin has changed or interpolation function has not been initialized, recompute interpolation function
        (i,j,k) = self.get_bin(lat,lon,z)
        if ( (i == self.i_cur) and (j == self.j_cur) and (k == self.k_cur) and (self.RH_interp != 0)):
            return self.RH_interp(lat,lon,z)
        else:
            (self.i_cur, self.j_cur, self.k_cur) = (i, j, k)
            self.RH_interp = self.get_var_interp(i, j, k, self.RH_ar)
            return self.RH_interp(lat,lon,z)

    def get_orog(self, lat, lon):
        """return interpolated ground height (m) at lat(deg), lon(deg)"""
        #if (i,j,k) bin has changed or interpolation function has not been initialized, recompute interpolation function
        (i,j,k) = self.get_bin(lat,lon,0, twod = True)
        if ( (i == self.i_cur) and (j == self.j_cur) and (self.orog_interp != 0)):
            # if(math.isnan(self.orog_interp(lat,lon))):
            #     print lat, lon, self.orog_interp(lat,lon)
            return self.orog_interp(lat,lon)
        else:
            (self.i_cur, self.j_cur) = (i, j)
            self.orog_interp = self.get_orog_interp(i, j, self.g_ar)
            if(math.isnan(self.orog_interp(lat,lon))):
               print(lat, lon, self.orog_interp(lat,lon))
               sys.exit()
            return self.orog_interp(lat,lon)


    def get_P_sat(self, T):
        """return water saturation pressure (Pa) at a given temperature T(K)"""
        T -= 273.15
        return 0.61078*math.exp(17.27*T/(T+243.04))*1000

    def get_rho(self, lat, lon, z):
        """return interpolated density (kg/m^3) at lat(deg), lon(deg), z(m)"""
        P = self.get_P(lat, lon, z)
        T = self.get_T(lat, lon, z)
        RH = self.get_RH(lat, lon, z)/100.
        P_H2O = RH*self.get_P_sat(T)
        return ((P - P_H2O)*M_AIR + P_H2O*M_H2O)/(RU*T)

# lat_range = (-10, 50)
# lon_range = (250, 350)
# now = datetime.now()
# hr = 0
# date_hr = "%d%02d%02d%02d" % (now.year, now.month, now.day, hr)
# #atmosphere.download_file(lat_range, lon_range, date_hr, "file.anl")
# # atm = atmosphere()
# # print atm.g_ar.shape
# d = np.zeros((2,100))
# print atm.get_orog(20.0, 275.0)
# for (i,l) in enumerate(np.linspace(5., 20., 100)):
#     d[0,i] = l
#     d[1,i] = atm.get_orog(l,275)
# print atm.g_ar[atm.i_cur-10:atm.i_cur,25]
# plt.plot(d[0,:], d[1,:], ".")
# print atm.i_cur, atm.j_cur
# print atm.g_ar.size
# print atm.g_ar[39:49][atm.j_cur-1]
# plt.plot(atm.lat_ar[atm.i_cur-15:atm.i_cur,0], atm.g_ar[atm.i_cur-15:atm.i_cur,atm.j_cur])
#
#b = balloon(36.0104, 360-84.2696, 1000)
#d = np.zeros((2,100))
#
#
#
#for (i,h) in enumerate(np.linspace(600,14000, 100)):
#    d[1,i] = atm.get_rho(36, 275, h)
#    d[0,i] = h
#
##print atm.g_ar[atm.i_cur, atm.j_cur]
#plt.figure(figsize=(10,10))
#plt.plot(d[0,:], d[1,:])
#
#plt.plot(atm.h_ar[atm.i_cur,atm.j_cur,0:20], atm.RH_ar[atm.i_cur,atm.j_cur,0:20], "8")
#plt.show()
#
#T = np.linspace(297, 400, 20)
#P1 = np.zeros_like(T)
#for i in range(len(T)):
#    P1[i] = get_P_sat(T[i])
#
#
#
#plt.plot(T-273.15, np.log10(P1))
##plt.plot(T-273.15, P2/101325)
#plt.grid()

#plt.show()
#plt.plot(atm.h_ar[atm.i_cur,atm.j_cur,0:20], atm.levels[0:20], ".")



#print atm.i_cur, atm.j_cur, atm.k_cur
#print atm.g_ar[atm.i_cur,atm.j_cur]

#print atm.get_P(36.0104, 360-84.2696, 500)

#k = get_k(i, j, b.h, h_data, g_data)
#print g_data[i,j]
#print b.lat, b.lon
#print lat_ar[i,j], lon_ar[i,j]

#print i, j, lat_ar[i,j], lon_ar[i,j]



#get_u = get_interp_val(i, j, k, b.lat, b.lon, b.h, lat_ar, lon_ar, h_data, u_data)
#get_v = get_interp_val(i, j, k, b.lat, b.lon, b.h, lat_ar, lon_ar, h_data, v_data)
#get_T = get_interp_val(i, j, k, b.lat, b.lon, b.h, lat_ar, lon_ar, h_data, T_data)
#get_P = get_P_interp(i, j, k, b.lat, b.lon, b.h, lat_ar, lon_ar, h_data, levels)

#TODO
#handle ground
#check binning as balloon moves
#pressure interpolation


#grb = grbs[1]
#print grb.shortName, grb.name, grb.level
#grounddata = grb.values
#plt.pcolor(lon_ar, lat_ar, g_data)





#print levels
#n_levels = len(levels)
#levels.reverse()
#levels = levels[8:]
#print levels
##print levels
#grbs.seek(0)
#
#
#for g in grbs:
#    print g
##    print g.name, g.level
#    #if(g.shortName == "hgtsfc"): break
#

#

#
#
#grbs.seek(0)
#grb = grbs.select(name = "Geopotential Height", level =1)[0]
#data = grb.values
#
#data
#data = grb.values
#print data
#dsf

#grbs.seek(0)
#for v in variable_names:
#    for (i,l) in enumerate(levels):
#        grb = grbs.select(name = v, level = l)[0]
#        data = grb.values
##        if(v == "U component of wind"):
##            u_data[:,:,i] = data
##        elif (v == "V component of wind"):
##            v_data[:,:,i] = data
##        elif (v == "Temperature"):
##            T_data[:,:,i] = data
##        elif (v == "Geopotential Height"):
##            h_data[:,:,i] = data
#        if (v == "Geopotential Height"):
#            h_data[:,:,i] = data
#
#    lat_ar, lon_ar = grb.latlons()



#

#def get_rho(P, T):
#    return P/(RSP*T)
#
#P = get_P(b.lat, b.lon, b.h)
#T = get_T(b.lat, b.lon, b.h)
#u = get_u(b.lat, b.lon, b.h)
#v = get_v(b.lat, b.lon, b.h)
#rho = get_rho(P, T)
#print T, P, rho, u, v

#for g in grbs:
#    print g.name




#for l in levels:
#    grb = grbs.select(name = "U component of wind", level = 1000)[0]


#m=Basemap(projection='mill',lat_ts=10,llcrnrlon=lon.min(), \
#  urcrnrlon=lon.max(),llcrnrlat=lat.min(),urcrnrlat=lat.max(), \
#  resolution='c')
#
#x, y = m(lon,lat)
#
#cs = m.pcolormesh(x,y,data,shading='flat',cmap=plt.cm.jet)
#
#m.drawcoastlines()
#m.fillcontinents()
#m.drawmapboundary()
#m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0])
#m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])
#
#plt.colorbar(cs,orientation='vertical')
#plt.title('Example 2: NWW3 Significant Wave Height from GRiB')
#plt.rcParams["figure.figsize"] = [20,15]
#plt.show()

#
##
##
#mydate='20170907'
#url='http://nomads.ncep.noaa.gov:9090/dods/gfs_1p00/gfs'+ \
#    mydate+'/gfs_1p00_00z'
#
#urllib.urlretrieve(url, "recent.nc")
#
#
#cdf_file = nc4.Dataset(url)

#lat  = cdf_file.variables['lat'][:]
#lon  = cdf_file.variables['lon'][:]
#u_data = cdf_file.variables['ugrdprs'][0]
#v_data = cdf_file.variables['vgrdprs'][0]
#h_data = cdf_file.variables['hgtprs'][0]
#t_data = cdf_file.variables['tmpprs'][0]
#
#
###cdf_file.close()
###
#
#m=Basemap(projection='mill',lat_ts=10,llcrnrlon=180, \
#  urcrnrlon=lon.max(),llcrnrlat=0,urcrnrlat=60, \
#  resolution='c')
#
#x, y = m(*np.meshgrid(lon,lat))
#speed_data = np.sqrt(u_data*u_data + v_data*v_data)
#
#
#plt.figure()
#m.pcolormesh(x,y,t_data[10],shading='flat',cmap=plt.cm.jet)
#m.colorbar(location='right')
#m.drawcoastlines()
##m.fillcontinents()
#m.drawmapboundary()
#m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0])
#m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])
#plt.rcParams["figure.figsize"] = [20,15]
#plt.show()
