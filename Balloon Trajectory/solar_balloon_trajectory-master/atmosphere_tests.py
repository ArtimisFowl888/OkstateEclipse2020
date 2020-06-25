import atmosphere
import numpy as np
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap

#test: draw worldwide orog
def test_orog():
    lat_range = (-90, 90)
    lon_range = (0, 360)
    now = datetime.now()
    hr = 0
    date_hr = "%d%02d%02d%02d" % (now.year, now.month, now.day, hr)
    #atmosphere.atmosphere.download_file(lat_range, lon_range, date_hr, "file.anl")
    atm = atmosphere.atmosphere("file.anl")
    lon_range = np.linspace(atm.lon_min, atm.lon_max, atm.lon_max - atm.lon_min+1)
    lat_range = np.linspace(atm.lat_min, atm.lat_max, atm.lat_max - atm.lat_min+1)
    nx = len(lat_range)
    ny = len(lon_range)
    ground = np.zeros((nx,ny))
    for i in range(len(lat_range)):
        for j in range(len(lon_range)):
            ground[i][j] = atm.get_orog(lat_range[i], lon_range[j])
    fig, ax = plt.subplots(1,1)
    P = ax.pcolormesh(lon_range, lat_range, ground)
    m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,\
                llcrnrlon=0,urcrnrlon=360)
    m.drawcoastlines()
    fig.savefig("orog.png", dpi = 300)

def test_h_slice(atm, h, func, fname):
    lat_range = (-90, 90)
    lon_range = (0, 360)
    atm = atmosphere.atmosphere("file.anl")
    lon_range = np.linspace(atm.lon_min, atm.lon_max, 2*(atm.lon_max - atm.lon_min+1))
    lat_range = np.linspace(atm.lat_min, atm.lat_max, 2*(atm.lat_max - atm.lat_min+1))
    nx = len(lat_range)
    ny = len(lon_range)
    data = np.zeros((nx,ny))


    for i in range(len(lat_range)):
        for j in range(len(lon_range)):
            data[i][j] = func(lat_range[i], lon_range[j], h)

    fig, ax = plt.subplots(1,1)
    P = ax.pcolormesh(lon_range, lat_range, data)
    m = Basemap(projection='cyl', llcrnrlat=-90,urcrnrlat=90,\
                llcrnrlon=0,urcrnrlon=360)
    m.drawcoastlines()
    fig.savefig(fname, dpi = 300)

def test_lat_slice(atm, lat, func, fname):
    atm = atmosphere.atmosphere("file.anl")
    lon_range = np.linspace(atm.lon_min, atm.lon_max, 2*(atm.lon_max - atm.lon_min+1))
    h_range = np.linspace(0, atm.h_ar[0][0][-1], 2*len(atm.levels))

    nx = len(lon_range)
    ny = len(h_range)
    data = np.zeros((ny,nx))
    for i in range(len(lon_range)):
        for j in range(len(h_range)):
            data[j][i] = func(lat, lon_range[i], h_range[j])
    fig, ax = plt.subplots(1,1)
    P = ax.pcolormesh(lon_range, h_range, data)
    fig.colorbar(P, ax=ax)
    ax.set_ylabel("height (m)")
    ax.set_xlabel("log (deg)")
    ax.legend()
    fig.savefig(fname, dpi = 300)

def test_lon_slice(atm, lon, func, fname):
    atm = atmosphere.atmosphere("file.anl")
    lat_range = np.linspace(atm.lat_min, atm.lat_max, 2*(atm.lat_max - atm.lat_min+1))
    h_range = np.linspace(0, atm.h_ar[0][0][-1], 2*len(atm.levels))

    nx = len(lat_range)
    ny = len(h_range)
    data = np.zeros((ny,nx))
    for i in range(len(lat_range)):
        for j in range(len(h_range)):
            data[j][i] = func(lat_range[i], lon, h_range[j])
            #print(i,j, lat_range[i], h_range[j])
    fig, ax = plt.subplots(1,1)
    P = ax.pcolormesh(lat_range, h_range, data)
    fig.colorbar(P, ax=ax)
    ax.set_ylabel("height (m)")
    ax.set_xlabel("log (deg)")
    ax.legend()
    fig.savefig(fname, dpi = 300)


def test_var_interp(atm, var, func, lat, lon, height, folder):
    #demonstrate that variable temperpolation is valid between discrete points
    ground_h = atm.get_orog(lat, lon)
    (i,j,k) = atm.get_bin(lat, lon, ground_h + height)


    h1 = atm.h_ar[i,j,k]
    h2 = atm.h_ar[i,j,k+1]
    h3 = atm.h_ar[i,j,k+2]

    print(80*'-')
    print("z test")
    print("binned values:")
    print("%f %f %f" % (var[i,j,k], var[i,j,k+1], var[i,j,k+2]))
    print("interp values:")
    print("%f %f %f" % (func(lat,lon,h1), func(lat,lon,h2), func(lat,lon,h3)))
    print(80*'-')

    fig, ax = plt.subplots(1,1)
    discrete_x = [atm.h_ar[i,j,k], atm.h_ar[i,j,k+1], atm.h_ar[i,j,k+2]]
    discrete_u = [var[i,j,k], var[i,j,k+1], var[i,j,k+2]]
    cont_x = np.linspace(h1, h3, 50)
    cont_u = np.zeros_like(cont_x)
    for (m,x) in enumerate(cont_x):
        cont_u[m] = func(lat, j, x)
    ax.plot(discrete_x, discrete_u, ".")
    ax.plot(cont_x, cont_u)
    ax.set_ylabel("u (m/s)")
    ax.set_xlabel("h (m)")
    ax.grid()
    fig.savefig(folder+"/h_interp.png", dpi = 300)
    fig.clf()

    h1 = atm.h_ar[i,j,k]
    h2 = atm.h_ar[i+1,j,k]
    h3 = atm.h_ar[i+2,j,k]
    print(80*'-')
    print("Lat test")
    print("binned values:")
    print("%f %f %f" % (var[i,j,k], var[i+1,j,k], var[i+2,j,k]))
    print("interp values:")
    print("%f %f %f" % (func(lat,lon,h1), func(lat+1,j,h2), func(lat+2,j,h3)))
    print(80*'-')

    fig, ax = plt.subplots(1,1)
    discrete_u = [var[i,j,k], var[i+1,j,k], var[i+2,j,k]]
    discrete_x = [i,i+1,i+2]

    cont_x = np.linspace(i,i+2, 50)
    cont_u = np.zeros_like(cont_x)

    for (m,x) in enumerate(cont_x):
        if(x < i+1):
            dh = atm.h_ar[i+1,j,k] - atm.h_ar[i,j,k]
            height = dh*(x-i) + atm.h_ar[i,j,k]
        else:
            dh = atm.h_ar[i+2,j,k] - atm.h_ar[i+1,j,k]
            height = dh*(x-i-1) + atm.h_ar[i+1,j,k]
        cont_x[m] = x
        cont_u[m] = func(x-90, j, height)

    ax.plot(discrete_x, discrete_u, ".")
    ax.plot(cont_x, cont_u)
    ax.set_ylabel("u (m/s)")
    ax.set_xlabel("lat (deg)")
    ax.grid()
    fig.savefig(folder+"/lat_interp.png", dpi = 300)
    fig.clf()


    print(80*'-')
    h1 = atm.h_ar[i,j,k]
    h2 = atm.h_ar[i,j+1,k]
    h3 = atm.h_ar[i,j+2,k]
    print("Lon test")
    print("binned values:")
    print("%f %f %f" % (var[i,j,k], var[i,j+1,k], var[i,j+2,k]))
    print("interp values:")
    print("%f %f %f" % (func(lat,lon,h1), func(lat,lon+1,h2), func(lat,lon+2,h3)))
    print(80*'-')


    fig, ax = plt.subplots(1,1)
    discrete_u = [var[i,j,k], var[i,j+1,k], var[i,j+2,k]]
    discrete_x = [j,j+1,j+2]

    cont_x = np.linspace(j,j+2, 50)
    cont_u = np.zeros_like(cont_x)

    for (m,x) in enumerate(cont_x):
        if(x < j+1):
            dh = atm.h_ar[i,j+1,k] - atm.h_ar[i,j,k]
            height = dh*(x-j) + atm.h_ar[i,j,k]
        else:
            dh = atm.h_ar[i,j+2,k] - atm.h_ar[i,j+1,k]
            height = dh*(x-j-1) + atm.h_ar[i,j+1,k]
        cont_x[m] = x
        cont_u[m] = func(lat, x, height)

    ax.plot(discrete_x, discrete_u, ".")
    ax.plot(cont_x, cont_u)
    ax.set_ylabel("u (m/s)")
    ax.set_xlabel("lon (deg)")
    ax.grid()
    fig.savefig(folder+"/lon_interp.png", dpi = 300)
    fig.clf()


def test_P_interp(atm, lat, lon, height, folder):
    #test: demonstrate that velocity interpolation is valid
    ground_h = atm.get_orog(lat, lon)
    (i,j,k) = atm.get_bin(lat, lon, ground_h + height)

    h1 = atm.h_ar[i,j,k]
    h2 = atm.h_ar[i,j,k+1]
    h3 = atm.h_ar[i,j,k+2]

    print(80*'-')
    print("z test")
    print("binned values:")
    print("%f %f %f" % (atm.levels[k]*100, atm.levels[k]*100, atm.levels[k+1]*100))
    print("interp values:")
    print("%f %f %f" % (atm.get_P(lat,j,h1), atm.get_P(lat,j,h2), atm.get_P(lat,j,h3)))
    print(80*'-')

    discrete_P = [atm.get_P(lat,j,h1), atm.get_P(lat,j,h2), atm.get_P(lat,j,h3)]
    discrete_x = [h1, h2, h3]
    cont_x = np.linspace(h1, h3, 50)
    cont_P = np.zeros_like(cont_x)

    for (m,x) in enumerate(cont_x):
        cont_P[m] = atm.get_P(lat, j, x)

    fig, ax = plt.subplots(1,1)
    ax.plot(cont_x, cont_P)
    ax.plot(discrete_x, discrete_P, ".")
    ax.grid()
    ax.set_facecolor((0.1,0.1,0.1))
    ax.set_xlabel("height (m)")
    ax.set_ylabel("Pressure (Pa)")
    fig.savefig(folder + "/P_vs_h.png", dpi = 300)


    discrete_P = [atm.get_P(lat,j,h1), atm.get_P(lat+1,j,h1)]
    discrete_x = [i, i+1]
    cont_x = np.linspace(lat, lat+1, 50)
    cont_P = np.zeros_like(cont_x)
    for (m,x) in enumerate(cont_x):
        cont_P[m] = atm.get_P(x, j, h1)

    fig, ax = plt.subplots(1,1)
    ax.plot(cont_x + 90, cont_P)
    ax.plot(discrete_x, discrete_P, ".")
    ax.grid()
    ax.set_facecolor((0.1,0.1,0.1))
    ax.set_xlabel("lat (deg)")
    ax.set_ylabel("Pressure (Pa)")
    fig.savefig(folder + "/P_vs_lat.png", dpi = 300)


    discrete_P = [atm.get_P(lat,j,h1), atm.get_P(lat,j+1,h1)]
    discrete_x = [j, j+1]
    cont_x = np.linspace(j, j+1, 50)
    cont_P = np.zeros_like(cont_x)
    for (m,x) in enumerate(cont_x):
        cont_P[m] = atm.get_P(lat, x, h1)

    fig, ax = plt.subplots(1,1)
    ax.plot(cont_x, cont_P)
    ax.plot(discrete_x, discrete_P, ".")
    ax.grid()
    ax.set_facecolor((0.1,0.1,0.1))
    ax.set_xlabel("lon (deg)")
    ax.set_ylabel("Pressure (Pa)")
    fig.savefig(folder + "/P_vs_lon.png", dpi = 300)



#now = datetime.now()
#hr = 0
#date_hr = "%d%02d%02d%02d" % (now.year, now.month, now.day, hr)
#atmosphere.atmosphere.download_file(lat_range, lon_range, date_hr, "file.anl")
atm = atmosphere.atmosphere("file.anl")
lat = 34.0
lon = 180.-106
#print(atm.lat_min, atm.lat_max)
#print(atm.lon_min, atm.lon_max)


# test_var_interp(atm, atm.u_ar, atm.get_u, lat, lon, 2000, "u_imgs")
# test_var_interp(atm, atm.v_ar, atm.get_v, lat, lon, 2000, "v_imgs")
# test_var_interp(atm, atm.T_ar, atm.get_T, lat, lon, 2000, "T_imgs")
# test_P_interp(atm, lat, lon, 2000, "P_interp")

#test_h_slice(atm, 5000, atm.get_P, "slices/P_slice.png")
#test_h_slice(atm, 5000, atm.get_u, "slices/u_slice.png")
#test_h_slice(atm, 5000, atm.get_v, "slices/v_slice.png")
#test_h_slice(atm, 5000, atm.get_T, "slices/T_slice.png")

#test_lat_slice(atm, 45.0, atm.get_u, "slices/u_slice.png")
#test_lat_slice(atm, 45.0, atm.get_v, "slices/v_slice.png")
#test_lat_slice(atm, 45.0, atm.get_v, "slices/T_slice.png")
#test_lat_slice(atm, lat, atm.get_P, "slices/P_slice_lat.png")
test_lon_slice(atm, lon, atm.get_P, "slices/P_slice_lon.png")
#test_h_slice(atm, 5000, atm.get_u, "slices/u_slice.png")
# test_h_slice(atm, 5000, atm.get_v, "slices/v_slice.png")
# test_h_slice(atm, 5000, atm.get_T, "slices/T_slice.png")

#test_P_interp()
