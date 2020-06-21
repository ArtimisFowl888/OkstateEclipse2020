import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import griddata, interp1d
from scipy.integrate import odeint
import math

class Glider:
    def __init__(self):
        self.name = None
        self.simtime = 0
        self.flightPath = []
        self.name = None
        self.AR = 0
        self.g = 0
        self.mass = 0
        self.CDo = 0
        self.e = 0
        self.atmosphere = Atmosphere()
        self.S = 0


    # Glider Performance, MaxGlideRatio, Return Home are all identical or very slight variations to Dela's Code
    def GliderPerformance(self, alpha, gc, rho, payload, windspeed):
        g = self
        eps = 1/ (np.pi * g.e * g.AR)
        CLa = np.pi * g.AR / (1+np.sqrt(1+ (g.AR/2)**2))
        CL = CLa * alpha
        CD = g.CDo + eps * CL**2
        totalmass = g.mass + payload

        num = 4*gc**2 + totalmass**2
        denom = (CD*g.S*rho)**2  + (CL*g.S*rho)**2
        V = (num/denom)**.25
        Gam = -np.arcsin((0.5*CD*g.S*V**2*rho)/ (gc*totalmass))
        xdot = V * np.cos(Gam)
        ydot  = V*np.sin(Gam)
        glideRatio = -(xdot-windspeed)/ydot
        groundSpeed = xdot - windspeed
        return xdot,ydot,glideRatio,groundSpeed

    def MaxGlideRatio(self,gc,rho,payload,windspeed,alphaGuess):
        def objective(alpha):
            glideRatio = self.GliderPerformance(alpha[0],gc,rho,payload,windspeed)[2]
            return -glideRatio

        answer = minimize(objective, [alphaGuess],method = 'Nelder-Mead')
        return float(answer.x),-answer.fun

    def ReturnHome(self,altitude,distance,winds,payload,maxtime,npoints):
        def ode_system(X,t):
            nonlocal  alphaGuess
            x = X[0];y = X[1];

            atm = self.atmosphere

            if y < 0: y = 0
            windspeed = float(griddata(np.array(winds.altitudes), np.array(winds.speeds), y))
            gc = float(griddata(atm.hdata, atm.gdata,y))
            rho = float(griddata(atm.hdata,atm.rhodata,y))

            alpha = self.MaxGlideRatio(gc, rho,payload, windspeed,alphaGuess)[0]
            alphaGuess = alpha
            xdot,ydot,glideRatio,groundSpeed = self.GliderPerformance(alpha,gc,rho,payload,windspeed)

            return [-groundSpeed,ydot]
        alphaGuess = 0.1
        t = np.linspace(0,maxtime,npoints)
        ic = [distance, altitude]
        xy = RK4(ode_system,ic,t)
        for i in range(len(xy)): # cutoff if glider hits the ground
            if xy[i,1] < 0:
                t = t[0:i+1]
                xy = xy[0:i+1,:]
                break
        for i in range(len(xy)):
            if xy[i,0]<0:
                t = t[0:i+1]
                xy = xy[0:i+1,:]
                break
        self.simtime = t
        self.flightPath = xy


class Winds:
    def __init__(self):
        self.name = None
        self.altitudes = []
        self.speeds = []


class Balloon:
    def __init__(self):
        self.name = None
        self.mass = None
        self.uninflatedDia = None
        self.burstDia = None


class Atmosphere:
    def __init__(self):
        self.hdata, self.tCdata, self.gdata, self.pdata, self.rhodata, self.mudata = np.loadtxt("US Standard Air Properties.txt", skiprows=4, unpack=True)


class BalloonFlight:
    def __init__(self):
        self.title = None
        self.winds = []; self.wind = None
        self.gliders = []; self.glider = None
        self.balloons = []; self.balloon = None
        self.maxtime = 0
        self.maxiter = 0
        self.paymass = 0
        self.altitude = 0
        self.launchDiam = 0
        self.maxaltitude = 0
        self.defGliderName = None
        self.defWindname = None
        self.defBalloonName = None
        self.atmosphere = Atmosphere()
        self.bflightpath = []
        self.distance = 0
        self.massGass = 0
        self.finaldiameter = 0
        self.setwname = None
        self.setbname = None
        self.setgname = None
        self.DOY = None
        self.TOD = None
        self.Lat = None
        self.area = 0
        self.tchange = 0
        self.d = 0
        self.TempChange = 0

    # flight sim system
    def flightsim(self, maxtime, maxalt=None, npoints=600):
        self.UpdateConnections()
        t = np.linspace(0, maxtime, npoints)
        self.tchange = t[1] - t[0]
        ic = [0, 0, 0, 0]
        #deltat = maxtime/npoints

        def ode_system(X,t):
            x=X[0]; xdot = X[1]; y = X[2]; ydot = X[3]

            if y > self.maxaltitude: y = self.maxaltitude # Cap y at maxalt
            # wind velocity
            vw = griddata(np.array(self.wind.altitudes), np.array(self.wind.speeds), y)
            vRel = np.sqrt((xdot-vw)**2+ydot**2)
            # Get dynamic forces
            lift, drag, g = self.Forces(vRel, y)
            # Total mass (mass of helium calculated in forces)
            mass = self.paymass + self.glider.mass + self.balloon.mass + self.masshel
            # Dynamic Force Balance Equations
            xddot = (-drag*(xdot-vw)/vRel)/mass
            yddot = (-drag*ydot/vRel - mass*g + lift)/mass
            return[xdot, xddot, ydot, yddot]

        xy = odeint(ode_system,ic,t) # matrix of observed dynamic parameters

        for i in range(len(xy)): # cutoff once balloon reaches max altitude
            if xy[i,2] > maxalt:
                t = t[0:i+1]
                xy = xy[0:i+1,:]
                break

        self.distance = float(xy[len(xy)-1,0])  # Get total distance traveled
        self.bflightpath = xy   # Store xy matrix in class object
        self.simtime = t    # Store time matrix in class object
        self.glider.ReturnHome(maxalt,self.distance,self.wind,self.paymass,maxtime,npoints) # Run Glider Simulation


    def Forces(self,Vrel,altitude):
        Rhel = 2077; Rair = 287 # Gas Constants
        atm = self.atmosphere   # Create atmosphere
        g = float(griddata(atm.hdata, atm.gdata, altitude)) # gravity
        rhoair = float(griddata(atm.hdata, atm.rhodata, altitude))
        pressure = float(griddata(atm.hdata, atm.pdata, altitude))*1e4
        T = float(griddata(atm.hdata, atm.tCdata, altitude))
        T += 273.15     # Convert Temperature to Kelvin

        if altitude == 0: # First Pass
            self.area = (self.launchDiam ** 2) * np.pi / 4
            volume = (self.launchDiam ** 3) * np.pi / 6
            self.d = self.launchDiam
            self.masshel = GasMass(pressure, volume, Rhel, T) # Storage of the mass of helium

        else: # Not First Pass
            self.Irradiation(pressure)
            T += self.TempChange
            volume = GasVolume(pressure, self.masshel, Rhel, T)
            self.d = (6 * volume / np.pi) ** (1 / 3)
            self.area = (self.d ** 2) * np.pi / 4

        mass = GasMass(pressure, volume, Rair, T) # Mass of displaced air

        if self.d > self.finaldiameter: self.finaldiameter = self.d  # Update diameter size

        lift = mass * g # lift = gravity * mass of displaced air
        Re = rhoair * Vrel * self.d / (float(griddata(atm.hdata, atm.mudata, altitude)) * 1e-5)  # Old School Reynold's calculation (All the cool kids use nu these days)
        Cd = CDSphere(Re) # Balloon Drag Coefficient
        drag = self.area * Cd * (Vrel ** 2) * rhoair * .5 # Drag = DragCoefficient*DynamicPressure*FrontalArea
        return lift, drag, g

    def Irradiation(self, pressure):
        tod = self.TOD*(360/24)*(np.pi/180)
        lat = self.Lat*(np.pi/180)
        C = self.DOY*(360/365)*(np.pi/180)
        d= 0.39637 - 22.9133*np.cos(C)+4.02543*np.sin(C)-0.3872*np.cos(2*C)+0.052*np.sin(2*C)
        b = np.arcsin(np.sin(lat)*np.sin(d)-np.cos(lat)*np.cos(d)*np.cos(tod))
        zeta = (np.pi/2)-b

        Pz = pressure
        Po = 10.13e4                                                    # atmospheric pressure at zero altitude N/m^2
        ma = (Pz/Po)*math.sqrt(1229+(614*np.cos(zeta))**2)+614*np.cos(zeta)
        Tatm = 0.5*(np.exp(-0.65*ma)+np.exp(-0.095*ma))
        a = self.DOY/365
        e = 0.016708
        Iso = 1358*(1+0.5*(((1+e)/(-2))**2-1)*np.cos(a))
        Is = Tatm*Iso
        Qdot = Is*self.area    # Objects have been made in the class for the values
        Q = Qdot/self.masshel
        self.TempChange += (Q/.005193) * self.tchange
        return

    def ReadBalloonData(self,data):
        for line in data:
            cells = line.strip().split(',')
            keyword = cells[0].lower()
            if keyword == 'title':
                self.title = cells[1].replace("'","")


            if keyword == 'simulation':
                self.defBalloonName = cells[1].strip()
                self.launchDiam = float(cells[2])
                self.defGliderName = cells[3].strip()
                self.defWindname = cells[4].strip()
                self.paymass = float(cells[5])
                self.altitude = float(cells[6])


            if keyword == 'simcontrol':
                self.maxtime = cells[1].strip()
                self.maxiter = cells[2].strip()

            if keyword == 'glider':
                thisglider = Glider()
                thisglider.name = cells[1].strip()
                thisglider.S = float(cells[2])
                thisglider.AR = float(cells[3])
                thisglider.e = float(cells[4])
                thisglider.mass = float(cells[5])
                thisglider.CDo = float(cells[6])
                self.gliders.append(thisglider)

            if keyword == 'windlib':
                thiswind = Winds()
                thiswind.name = cells[1].strip()
                thiswind.altitudes = []
                thiswind.speeds = []
                for i in range(2,len(cells)):
                    if i %2 == 0:
                        thiswind.altitudes.append(float(cells[i].replace('(',"")))
                    else:
                        thiswind.speeds.append(float(cells[i].replace(')',"")))
                self.winds.append(thiswind)

            if keyword == 'balloonlib':
                thisballoon = Balloon()
                thisballoon.name = cells[1].strip()
                thisballoon.mass = float(cells[2])
                thisballoon.uninflatedDia = float(cells[3])
                thisballoon.burstDia = float(cells[4])
                self.balloons.append(thisballoon)


    def UpdateConnections(self):
        # get the objects based on combobox selections
        for Wind in self.winds:
            self.wind = FindItemByName(self.setwname,self.winds)
        for Balloon in self.balloons:
            self.balloon = FindItemByName(self.setbname,self.balloons)
        for Glider in self.gliders:
            self.glider = FindItemByName(self.setgname,self.gliders)

    def GererateReport(self):
        report = '\tStratoGlider Flight Performance'  # Header
        report += '\n\nTitle: ' + self.title
        # User inputs
        report += '\nBalloon Name: ' + str(self.setbname)
        report += '\nLaunch Diameter: ' + str(self.launchDiam) + ' meters'
        report += '\nPayload Mass:\t' + str(self.paymass) + ' kg'
        report += '\nWind Condition: ' + str(self.setwname)
        report += '\nGlider Deployment altitude: ' + str(self.maxaltitude) + ' meters'
        report += '\nGlider Name: ' + str(self.setgname)
        # Balloon Flight Summary
        report += '\n\n'
        report += '\tBalloon at Deployment Altitude'
        report += '\n\n'
        report += 'Flight Time: '+ str(self.simtime[len(self.simtime)-1].round(1)) + ' seconds'
        report +='\nGround Distance Traveled: {:.1f} meters'.format(self.distance)
        report +='\nFinal Diameter: {:.1f} meters,\tBurst Diameter: {:.1f} meters'.format(self.finaldiameter,self.balloon.burstDia)
        # Glider Flight Summary
        report += '\n\n\tGlider Return Flight'
        report += '\n\n'
        if self.glider.flightPath[len(self.glider.flightPath)-1,1] < 0: # If the Glider fails to return to launch
            report += 'Glider cannot return to launch site!'
            report += '\n       It flys for {:.1f} meters'.format(self.glider.simtime[len(self.glider.simtime)-1])
            report += '\n       It reaches the ground {:.1f} meters away from the launch site'.format(self.glider.flightPath[len(self.glider.flightPath)-1,0])
        else: # Mission was a success
            report += 'Glider can return to launch site!'
            report += '\n       It flys for {:.1f} seconds'.format(self.glider.simtime[len(self.glider.simtime)-1])
            report += '\n       It arrives above the launch site {:.1f} meters altitude'.format(self.glider.flightPath[len(self.glider.flightPath)-1,1])
        return report


def FindItemByName(name, objectlist):
    # search a list of objects to find one with a particular name
    # of course, the objects must have a "name" member
    for item in objectlist:  # all objects int he list
        if item.name == name:  # does it have the name I am seeking?
            return item  # then return this one
    # next item
    return None  # couldn't find it


def FindAltitudeIndex(xy,altitude):
    for i in range(len(xy)):
        if xy[i,2]>altitude: return i
    return len(xy) - 1

def GasVolume(pressure,mass,R,T):
    #IGL
    v = mass*R*T/pressure       # Kelvin conversion happens earlier now
    return v

def GasMass(pressure,volume,R,T):
    mass = pressure*volume/(R*T)        # Kelvin conversion happens earlier now
    return mass

def CDSphere(Re):
    # from "Drag coefficient of flow around a sphere: Matching asymptotically the wide trend"
    phi1 = (24/Re)**10 + (21*Re**(-.67))**10 + (4*Re**(-.33))**10 + 0.4**10
    phi2 = 1/ (((0.148*Re**.11)**(-10))+.5**(-10))
    phi3 = ((1.57*10**8)*(Re**(-1.625)))**10
    phi4 = 1/ ((6*(10**(-17)) * Re**2.63)**(-10) + .2**(-10))

    CD = ((1/(((phi1+phi2)**(-1)) + (phi3**(-1)))) + phi4)**(1/10)
    return CD


def RK4(func,ic,t):
    ntimes = len(t)
    nstates = len(ic)
    x = np.zeros((ntimes,nstates))
    x[0]=ic
    for i in range(len(t)-1):
        h = t[i+1]-t[i]
        k1 = h*np.array(func(x[i],t[i]))
        k2 = h*np.array(func(x[i]+k1/2, t[i]+h/2))
        k3 = h * np.array(func(x[i] + k2 / 2, t[i] + h / 2))
        k4 = h * np.array(func(x[i] + k3, t[i] + h))
        x[i+1] = x[i]+ (1/6)*(k1+2*k2+2*k3+k4)
        pass
    return x
