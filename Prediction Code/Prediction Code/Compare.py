import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

gfsData = np.genfromtxt('GFStest.txt', dtype=str, skip_header=1, usecols=(0,1,2,3), unpack=False)
lon1 = []
lat1 = []
alt1 = []
rise1 = []
for i in gfsData:
    lon1.append(float(i[0]))
    lat1.append(float(i[1]))
    alt1.append(float(i[2]))
    rise1.append(float(i[3]))
wrfData = np.genfromtxt('WRFtest.txt', dtype=str, skip_header=1, usecols=(0,1,2,3), unpack=False)
lon2 = []
lat2 = []
alt2 = []
rise2 = []
for i in wrfData:
    lon2.append(float(i[0]))
    lat2.append(float(i[1]))
    alt2.append(float(i[2]))
    rise2.append(float(i[3]))

def graphPath():
    plt.plot(lon1, lat1, '-r', label='GFS')
##    plt.scatter(lon1[0], lat1[0], color='r')
##    plt.plot(lon2, lat2, '-b', label='WRF')
##    plt.scatter(lon2[0], lat2[0])
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    plt.title('WRF vs GFS Prediction Path 2D')
    plt.legend(borderaxespad=0)
    plt.tight_layout()
    

def graphRiseRate():
    plt.plot(rise1, alt1, '-r', label='GFS')
##    plt.plot(rise2, alt2, '-b', label='WRF')
    plt.ylabel('Altitude (m)')
    plt.xlabel('Rise Rate (m/s)')
    plt.title('Rise Rate of Flight')
    plt.legend(borderaxespad=0)

def graphPath3D():
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot(lon1, lat1, alt1, '-r', label='GFS')
##    ax.plot(lon2, lat2, alt2, '-b', label='WRF')
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    ax.set_zlabel('altitude (m)')
    ax.set_title('WRF vs GFS Prediction Path 3D')
    ax.legend(borderaxespad=0)
    
graphPath()
##plt.figure()
##graphRiseRate()
graphPath3D()

plt.show()
