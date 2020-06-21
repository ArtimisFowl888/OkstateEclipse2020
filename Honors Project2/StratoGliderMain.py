import sys
import numpy as np
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QEvent
# Import Plotting Functions
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# the ui created by Designer and pyuic
from ProjectGUI import Ui_Dialog

# import the Problem Specific class
from StratoGliderClass import BalloonFlight

# this is just a test

class PlotCanvas(FigureCanvas):

    def __init__(self, parent, width=None, height=None, dpi=100):
        if width == None: width = parent.width()/100
        if height == None: height = parent.height()/100
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    # Balloon glider plots
    def plotit(self,bdata,gdata):
        self.figure.clf()
        ax = self.figure.add_subplot(111)
        bx = []; gx = []; by = []; gy= []
        for i in range(len(bdata)):
            bx.append(bdata[i,0])
            by.append(bdata[i,2])

        for i in range(len(gdata)):
            gx.append(gdata[i, 0])
            gy.append(gdata[i, 1])
        np.round(by, 1)
        np.round(bx, 1)
        np.round(gx, 1)
        np.round(gy, 1)
        ax.plot(gx,gy,'g',label='Glider')
        ax.plot(bx,by,'b',label='Balloon')
        ax.set_title('Balloon and Glider Flight Paths')
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.legend(loc='lower right')

        self.draw()

class PlotCanvas2(FigureCanvas):

    def __init__(self, parent, width=None, height=None, dpi=100):
        if width == None: width = parent.width()/100
        if height == None: height = parent.height()/100
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    #  balloon plots
    def plotit(self,bdata,t):
        self.figure.clf()
        x = [];xd = [];y = [];yd = []
        for i in range(len(bdata)):
            x.append(bdata[i, 0])
            y.append(bdata[i, 2])
            xd.append(bdata[i, 1])
            yd.append(bdata[i, 3])
        np.round(y ,1)
        np.round(x, 1)
        np.round(xd, 1)
        np.round(yd, 1)

        ax = self.figure.add_subplot(511)   # divides graphics view 5 times on the vertical starts at 1 on vertical has height of 1
        ax.plot(t,x,label='X')
        ax.plot(t,y,label = 'Y')
        ax.set_title('Balloon Flight X-Y')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('X and Y (m)')
        ax.legend(loc='upper left',prop={'size':8})

        bx = self.figure.add_subplot(513)
        bx.plot(t,xd,label = 'Xdot')
        bx.plot(t,yd,label = 'Ydot')
        bx.set_title('Balloon Flight Xdot-Ydot')
        bx.set_xlabel('Time (s)')
        bx.set_ylabel('Xdot and Ydot (m/s)')
        bx.legend(loc='upper right', prop={'size': 8})

        cx = self.figure.add_subplot(515)
        cx.plot(x,y)
        cx.set_title('Balloon Flight Path')
        cx.set_xlabel('x (m)')
        cx.set_ylabel('y (m)')

        self.draw()


class main_window(QDialog):
    def __init__(self):
        super(main_window, self).__init__()
        self.ui = Ui_Dialog()
        # setup the GUI
        self.ui.setupUi(self)
        self.BalloonFlight = None
        self.filename = None
        self.startupname = "Balloon 3.txt"
        gliderplot = self.ui.graphicsView_flightpath
        self.m = PlotCanvas(gliderplot)
        balloonpath = self.ui.graphicsView_balloonplots
        self.n = PlotCanvas2(balloonpath)

        self.assign_widgets()
        self.show()

    def assign_widgets(self):  # callbacks for Widgets on your GUI
        self.ui.pushButton.clicked.connect(self.ExitApp)
        self.ui.pushButton_Open.clicked.connect(self.GetData)
        self.ui.pushButton_Launch.clicked.connect(self.Launch)

    def GetData(self):
        if self.startupname!=None:      # Run file at startup
            self.filename = self.startupname
            self.startupname = None
        else:
            self.filename = QFileDialog.getOpenFileName()[0]
            if len(self.filename)==0:       # In case no file is selected
                no_file()
                return
        self.ui.textEdit_filename.setText(self.filename)  # Textbox = filename
        app.processEvents()

        # Read file
        f1 = open(self.filename,'r')
        data = f1.readlines()
        f1.close()

        self.BalloonFlight = BalloonFlight()
        bf = self.BalloonFlight

        bf.ReadBalloonData(data)
        # Clear existing values from cbs
        self.ui.comboBox_glider.clear()
        self.ui.comboBox_balloon.clear()
        self.ui.comboBox_wind.clear()
        # Fill CBs
        for i in range(len(bf.balloons)):
            self.ui.comboBox_balloon.addItem(bf.balloons[i].name)
        for i in range(len(bf.gliders)):
            self.ui.comboBox_glider.addItem(bf.gliders[i].name)
        for i in range(len(bf.winds)):
            self.ui.comboBox_wind.addItem(bf.winds[i].name)
        # Set defaults for CBs
        i = self.ui.comboBox_balloon.findText(bf.defBalloonName, Qt.MatchFixedString)
        self.ui.comboBox_balloon.setCurrentIndex(i)
        i = self.ui.comboBox_glider.findText(bf.defGliderName, Qt.MatchFixedString)
        self.ui.comboBox_glider.setCurrentIndex(i)
        i = self.ui.comboBox_wind.findText(bf.defWindname, Qt.MatchFixedString)
        self.ui.comboBox_wind.setCurrentIndex(i)
        # Rest of defaults in txt file
        self.ui.lineEdit_LaunchDia.setText(str(bf.launchDiam))
        self.ui.lineEdit_alt.setText(str(bf.altitude))
        self.ui.lineEdit_mass.setText(str(bf.paymass))

        self.ui.lineEdit_FlightTime.setText(str(bf.maxtime))
        self.ui.lineEdit_Steps.setText(str(bf.maxiter))

    def Launch(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        bf = self.BalloonFlight
        try:
            # Remapping defaults in case of user changes
            bf.launchDiam = float(self.ui.lineEdit_LaunchDia.text())
            bf.paymass = float(self.ui.lineEdit_mass.text())
            # Sim Control
            maxtime = float(self.ui.lineEdit_FlightTime.text())
            iterations = int(self.ui.lineEdit_Steps.text())
            bf.maxaltitude = float(self.ui.lineEdit_alt.text())
            # Mapping Names of selected combos at lauch
            bf.setwname = self.ui.comboBox_wind.currentText()
            bf.setbname = self.ui.comboBox_balloon.currentText()
            bf.setgname = self.ui.comboBox_glider.currentText()
            bf.TOD = float(self.ui.lineEdit_TimeofDay.text())
            bf.DOY = float(self.ui.lineEdit_DayofYear.text())
            bf.Lat = float(self.ui.lineEdit_Latitude.text())
            # Simulate Flight (This also calls glider calcs)
            bf.flightsim(maxtime, bf.maxaltitude, iterations)
            # Write Report
            report = bf.GererateReport()
            self.ui.plainTextEdit_FlightReport.setPlainText(report)
            # Show Graphs
            self.ShowPlot()
            QApplication.restoreOverrideCursor()
        except:
            QApplication.restoreOverrideCursor()
            bad_file()

    def ShowPlot(self):
        # Generate balloon flight plots
        self.m.plotit(self.BalloonFlight.bflightpath, self.BalloonFlight.glider.flightPath)
        # Generate glider/balloon flight plot
        self.n.plotit(self.BalloonFlight.bflightpath,self.BalloonFlight.simtime)

    def ExitApp(self):
        app.exit()

def no_file():
    msg = QMessageBox()
    msg.setText('There was no file selected')
    msg.setWindowTitle("No File")
    retval = msg.exec_()
    return None

def bad_file():
    msg = QMessageBox()
    msg.setText('Unable to process the selected file')
    msg.setWindowTitle("Bad File")
    retval = msg.exec_()
    return None


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    main_win = main_window()

    if main_win.startupname is not None:
        main_win.GetData()

    sys.exit(app.exec_())