# -*- coding: utf-8 -*-
#Fowler 7/19/16
from scipy import stats #Needed if use stats.linregress
import numpy as np
import matplotlib.pyplot as plt

#Read in a text file, genfrmtxt needs equally space lines in data or will give errors
#data = np.genfromtxt(open('edit_08212017_Center_Blaunch_Acer_181604.txt','U'), skip_header=2, unpack=False) #data To determine lapse rate cuts off PBL and Tropopause
#graphing files go from surface to 700 mbar.
data1816 = np.genfromtxt(open('graph_08212017_Center_Blaunch_Acer_181604.txt','U'), skip_header=2, unpack=False)
data1741 = np.genfromtxt(open('graph_08212017_Center_Blaunch_Acer_174108.txt','U'), skip_header=2, unpack=False)
data1706 = np.genfromtxt(open('graph_08212017_Center_Blaunch_Acer_170605.txt','U'), skip_header=2, unpack=False)
data1619 = np.genfromtxt(open('graph_08212017_Center_Blaunch_Acer_161904.txt','U'), skip_header=2, unpack=False)
data1146 = np.genfromtxt(open('graph_08212017_Center_Blaunch_Acer_114604.txt','U'), skip_header=2, unpack=False)

T1816 = data1816[:,2]
alt_km1816 = (data1816[:,8])/1000
P1816 = data1816[:,1]

T1741 = data1741[:,2]
alt_km1741 = (data1741[:,8])/1000
P1741 = data1741[:,1]

T1706 = data1706[:,2]
alt_km1706 = (data1706[:,8])/1000
P1706 = data1706[:,1]

T1619 = data1619[:,2]
alt_km1619 = (data1619[:,8])/1000
P1619 = data1619[:,1]

T1146 = data1146[:,2]
alt_km1146 = (data1146[:,8])/1000
P1146 = data1146[:,1]

#T = data[:,2]
#alt_km = data[:,10]

#statistics for lapse rate value using files starting with edit_
#slope, intercept, r_value, p_value, std_err=stats.linregress(T,alt_km) #This computes a least-squares regression for two sets of measurements.
slope_invert = 1/slope
#print(slope_invert)

slope,intercept=np.polyfit(T1816, alt_km1816, 1) #numpy.polyfit(x, y, deg, rcofull=False, w=None,
##cov=False)[source] Least squares polynomial fit. Fit a polynomial p(x) = p[0] * x**deg + ... + p[deg]
##of degree deg to points (x, y). Returns a vector of coefficients p that minimises the squared error.
##Uses np.linalg.lstsq(tt, y)

fit = (slope*T1816)+intercept #equation of function to plot fit.
##error in slope and intercept? - Make script/module to calculate uncertainties based on 444 handout.

#plt.plot(T, alt_km, 'r', Dp, alt_km, 'b', marker='.', markersize=8) #two variables
#plt.plot(T, alt_km, 'r', marker='.', markersize=8)

plt.plot(T1619, P1619, color='black', label='5min before C1')
plt.plot(T1706, P1706, color='red', label='40min before totality')
plt.plot(T1741, P1741, color='green', label='5min before totality')
plt.plot(T1816, P1816, color='blue', label='30min after totality') #Scatter plot x and y using blue circle markers
#plt.scatter(T1816, P1816, color='blue', marker = "o", label='30min after totality', s=.5) #Scatter plot x and y using blue circle markers
plt.gca().invert_yaxis() #plot pressure highest value to lowest value

#plt.plot(T, (slope*T)+intercept, color='green', linestyle='--', label='fit') #Plot of least squares fit.
##plt.axis() #xis() returns the current axes limits [xmin, xmax, ymin, ymax].
##plt.errorbar(tt, y, yerr=.05, xerr=None, fmt=None, label='_nolegend') #errorbar(x, y, yerr=None (could put in array like y or tt), xerr=None,
##fmt='-', ecolor=None, elinewidth=None, capsize=3,barsabove=False, lolims=False,
##uplims=False, xlolims=False, xuplims=False)

plt.xlabel('Temperature (C)', fontsize=14) #x-axis label
plt.ylabel('Pressure (mbar)', fontsize=14) #y-axis label

plt.title('8/21/17 Center Site Fort Laramie, WY', fontsize=12) #plot title

plt.annotate('Lapse Rate (C/Km) = {0:.4f}'.format(slope_invert), (0.09, 0.05), xycoords='axes fraction')
# pyplot.annotate lets you put text on the figure in a variety of ways such as adding slope. Here,
#I’ve set the xycoords parameter to “axes fraction” so that annotate interprets my coordinates (0.05, 0.9) as fractions between 0 and 1 relative to the figure axes. The (0.05, 0.9) means to place the
#text horizontally 5% from the y-axis (left) and 90% from the x-axis (bottom).
    
plt.legend(loc='upper right', bbox_to_anchor = (0.90, 0.90), frameon=False) #puts legend identified by label in scatter and plot

#plt.show() #display all figures

plt.savefig('centersite_plots.pdf') #Saves the plot.


