from Tkinter import *
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.basemap import Basemap
import WRFPrediction
import numpy as np


class App:
    
    def __init__(self, master):
        self.master = master
        
        self.lat = 46.8601
        self.lon = -113.9852
        self.alt = 978
        self.burst = 25000
        self.wrf = 'wrfout_d02_2015-06-23_12:00:00'
        self.dir = '/home/jaylene/Documents/WRF/WRFV3/test/em_real/'

        frame = Frame(master)
        frame.grid()
        
        #Latitude
        self.llat = Label(frame, text='Starting Latitude:')
        self.llat.grid(row=0, sticky=W)
        self.elat = Entry(frame, width=50)
        self.elat.grid(row=0, column=1)
        self.elat.insert(0, self.lat)
        
        #Longitude
        self.llon = Label(frame, text='Starting Longitude:')
        self.llon.grid(row=1, sticky=W)
        self.elon = Entry(frame, width=50)
        self.elon.grid(row=1, column=1)
        self.elon.insert(0, self.lon)
        
        #Starting Altitude
        self.lalt = Label(frame, text='Starting Altitude:')
        self.lalt.grid(row=2, sticky=W)
        self.ealt = Entry(frame, width=50)
        self.ealt.grid(row=2, column=1)
        self.ealt.insert(0, self.alt)
        
        #Bust Altitude
        self.lburst = Label(frame, text='Burst Altitude:')
        self.lburst.grid(row=3, sticky=W)
        self.eburst = Entry(frame, width=50)
        self.eburst.grid(row=3, column=1)
        self.eburst.insert(0, self.burst)

        #WRF File
        self.lwrf = Label(frame, text='WRF File Name:')
        self.lwrf.grid(row=4, sticky=W)
        self.ewrf = Entry(frame, width=50)
        self.ewrf.grid(row=4, column=1)
        self.ewrf.insert(0, self.wrf)

        #WRF Directory
        self.ldir = Label(frame, text='WRF Directory:')
        self.ldir.grid(row=5, sticky=W)
        self.edir = Entry(frame, width=50)
        self.edir.grid(row=5, column=1)
        self.edir.insert(0, self.dir)

        #Prediction Button
        self.bpredict = Button(frame, text='Prediction', command=self.callback)
        self.bpredict.grid(row=6, column=1)

        #Landing Location
        self.lland = Label(frame, text='Landing Location:')
        self.lland.grid(row=7, sticky=W)
        self.v = StringVar()
        self.lcoord = Label(frame, textvariable=self.v)
        self.lcoord.grid(row=7, column=1, sticky=W)

        #Map Graph
        f = Figure(figsize=(5,5), dpi=100)
        self.ax1 = f.add_subplot(111)
        self.m = Basemap(width=400000, height=400000, projection='lcc', lon_0=self.lon, lat_0=self.lat, resolution='i', ax=self.ax1)
        self.m.drawcoastlines()
        self.m.drawcountries()
        self.m.drawstates()
        self.m.fillcontinents(color='#cc9966', lake_color='#99ffff')
        self.canvas = FigureCanvasTkAgg(f, master)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0, column=3)

    def callback(self):
        self.lat = float(self.elat.get())
        self.lon = float(self.elon.get())
        self.alt = float(self.ealt.get())
        self.burst = float(self.eburst.get())
        self.wrf = self.ewrf.get()
        self.dir = self.edir.get()
        points = WRFPrediction.Prediction(self.wrf, self.dir, self.lat, self.lon, self.alt,self.burst)
        self.ax1.clear()
        self.Plotting(points)
        self.canvas.show()

    def Plotting(self, points):
        points = np.array(points)
        x = points[:,1]
        y = points[:,0]
        z = points[:,2]
        self.m = Basemap(width=400000, height=400000, projection='lcc', lon_0=points[0][1], lat_0=points[0][0], resolution='i', ax=self.ax1)
        self.m.drawcoastlines()
        self.m.drawcountries()
        self.m.drawstates()
        self.m.fillcontinents(color='#cc9966', lake_color='#99ffff')
        x,y = self.m(x,y)
        self.m.plot(x,y, 'r-')
        for i in range(len(z)-1):
            if z[i+1] < z[i]:
                self.m.plot(x[i], y[i], 'bo')
                break
        self.v.set(str(points[len(y)-1,0]) + ', ' + str(points[len(x)-1,1]))




root = Tk()

app = App(root)

root.mainloop()
