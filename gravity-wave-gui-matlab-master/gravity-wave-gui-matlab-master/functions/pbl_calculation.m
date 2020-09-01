
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%           PBL Height Determination with 3 Different Methods             %        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%
% This code calculates planetary boundary height (PBL) using three 
% different methods. Each method outputs a height and the methods are 
% plotted with the PBLHs found. 
%
% The first method is the Richardson number method. The PBL height is
% defined to be the lowest altitude where richardson number Ri(z) = 0.25. 
% 
% The second methd is the potential temperature gradient method. The
% vertical gradient of potential temperature is calculated and the maximum
% of the gradient is defined as the PBL height.
%
% The third method is the specific humidity gradient method. The vertical
% gradient of specific humidity is calculated and the minimum of the
% gradient is defined as the PBL height. 
%
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                         Set up input prompt window                      %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


function [PBLpt, PBLri, PBLsh, type] = pbl_calculation(fullfilename, ch1_pt, ch2_ri, ch3_sh, ax_1, ax_2, ax_3, ax_4)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                               Pull Data                                 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Get Data from File
data = readSondeFile(fullfilename); 

% Get data from table
[tempc, temp, alt, height, p, h, w, th] = get_data(data);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                               Calculations                              %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Calculate richardson number
[PBLri, pt, rv, ri] = ri_method(tempc, temp, alt, height, p, h, w , th);

% Calculate PBLH from potential temperature method
[PBLpt, dpt] = pt_method(height, pt);

% Calculate PBLH from specific humidity method
[PBLsh, dsh] = sh_method(height, rv);

% Find layer stability
[type] = layer_stability(height,pt);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                 Plotting                                %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% if y, this plots vertical gradient of potential temperature with PBLHs
if ch1_pt
    if isempty(ax_1)
        f1 = figure();
        ax_1 = axes(f1);
    end
    cla(ax_1)
    plot(ax_1, dpt,height)
    hold(ax_1, 'on')
    pt_line1 = yline(ax_1, PBLpt,'g','DisplayName','\theta Method');
    ri_line1 = yline(ax_1, PBLri, 'r', 'DisplayName','Ri Method');
    sh_line1 = yline(ax_1, PBLsh,'b','DisplayName','Specific Hu Method');
    hold(ax_1, 'off')
    title(ax_1, 'Vertical Gradient of Potential Temperature')
    xlabel(ax_1,'Potential Temp (K) per Meter')
    ylabel(ax_1,'Height (m)')
    legend(ax_1,[pt_line1,ri_line1,sh_line1])
    axis(ax_1, [-0.1,0.1,0,4000])
else
    cla(ax_1)
end

% if y, this plots Height vs Richardson number with PBLHs
if ch2_ri
    if isempty(ax_2)
        f2 = figure();
        ax_2 = axes(f2);
    end
    cla(ax_2)
    plot(ax_2, ri,height)
    hold(ax_2, 'on')
    ri_line2 = yline(ax_2, PBLri,'r','DisplayName','Ri Method');
    sh_line2 = yline(ax_2, PBLsh,'b','DisplayName','Specific Hu Method');
    pt_line2 = yline(ax_2, PBLpt, 'g', 'DisplayName','\theta Method');
    xline(ax_2, 0.25, 'DisplayName','Ri(z)=0.25');
    hold(ax_2, 'off')
    title(ax_2, 'Height vs Richardson Number')
    xlabel(ax_2,'Richardson Number')
    ylabel(ax_2, 'Height (m)')
    legend(ax_2, [pt_line2,ri_line2,sh_line2])
    axis(ax_2, [-3,3,0,4000])
else
    cla(ax_2)
end

% if y, this plots vertical gradient of specific humidity with PBLHs
if ch3_sh
    if isempty(ax_3)
        f3 = figure();
        ax_3 = axes(f3);
    end
    cla(ax_3)
    plot(ax_3, dsh,height)
    hold(ax_3, 'on')
    sh_line3 = yline(ax_3, PBLsh,'b','DisplayName','Specific Hu Method');
    ri_line3 = yline(ax_3, PBLri,'r','DisplayName','Ri Method');
    pt_line3 = yline(ax_3, PBLpt, 'g', 'DisplayName','\theta Method');
    hold(ax_3, 'off')
    title(ax_3, 'Vertical Gradient of Specific Humidity')
    xlabel(ax_3,'Specific Humidity per Meter')
    ylabel(ax_3,'Height (m)')
    legend(ax_3,[pt_line3,ri_line3,sh_line3])
    axis(ax_3, [-0.000035,0.000035,0,4000])
else
    cla(ax_3)
end 

% Plots height vs. potential temp and temp in Kelvin with PBLHs
if isempty(ax_4)
    f4 = figure();
    ax_4 = axes(f4);
end
cla(ax_4)
plot(ax_4, pt,height)
hold(ax_4, 'on')
plot(ax_4, temp,height)
pt_line4 = yline(ax_4, PBLpt,'g','DisplayName','\theta Method');
ri_line4 = yline(ax_4, PBLri,'r','DisplayName','Ri Method');
sh_line4 = yline(ax_4, PBLsh,'b','DisplayName','Specific Hu Method');
hold(ax_4, 'off')
title(ax_4, 'Potential Temperature & Temperature (K)')
xlabel(ax_4,'Potential Temperature & Temperature (K)')
ylabel(ax_4, 'Height (m)')
legend(ax_4, [pt_line4,ri_line4,sh_line4])
axis(ax_4, [280,320,0,4000])


%Print Message box with PBL heights and Layer stability info
% msgbox(sprintf('The atmosphere possesses a %s\n\n\t\tPBL heights:\n\nRichardson Method: %.2f m \n\nPotential T Method: %.2f m \n\nSpecific Humidity Method: %.2f m\n\n%s',type,PBLri,PBLpt,PBLsh))

end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                               Functions                                 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [tc, tk, a, hi, pr, hu, ws, wd] = get_data(dat)

% This function extracts the needed data from the data table. 
% Input is is a data table, output is arrays of data


tc = dat.T;  %Temperature in Celcious
a = dat.Alt; %Altitude in meters (MSL)
pr = dat.P;     %Pressure in hPA
hu = dat.Hu*0.01; %relative humidity (decimal not percent)
ws = dat.Ws;    %Wind speed in m/s
wd = dat.Wd;   %Wind direction in degrees

tk = tc+273.15; %Temperature in Kelvin
hi = a-a(1); %height above ground in meters

end


function [pblri, pot, rvv, ri] = ri_method(tc, tk, a, hi, pr, hu, ws, wd)

% This function calculates richardson number along with the variables (like
% potential temperature) needed to calculate richardson number. It then
% searches for where Ri(z) is near 0.25 and interpolates to get the height
% z where Ri(z) = 0.25.
%
% INPUTS: temperature in C, temperature in K, altitude in meters, height in
% meters, pressure in hPa, humidity as decimal value, wind speed in m/s,
% and wind direction in degrees.
%
% OUTPUTS: PBL height, potential temperature, water vaport mixing ratio, and
% richardson number 

%epsilon, unitless constant
epsilon = 0.622; 

%saturation vapor pressure
es = 6.1121*exp((18.678-(tc/234.84)).*(tc./(257.14+tc))); %hPa

%vapor pressure
e = es.*hu; %hPa

%water vapor mixing ratio
rvv = (epsilon*e)./(pr-e); %unitless

%potential temperature
pot = (1000.0^0.286)*tk./(pr.^0.286); %kelvin

%virtual potential temperature
vpt = pot.*((1+(rvv./epsilon))./(1+rvv)); %kelvin

%component wid speeds, m/s
u = ws.*cos(deg2rad(wd)); 
v = ws.*sin(deg2rad(wd));

a0 = a(1); %surface altitude
vpt0 = vpt(1); %virtual potential temperature at surface
g = 9.81;

%Richardson number. If surface wind speeds are zero, the first data point
%will be an inf or NAN.
ri = (((vpt-vpt0)./vpt0).*(a-a0)*g)./((u).^2+(v).^2);


%Look if zero surface wind speeds make first point inf/Nan then replace
%with point above. Assumes only inf/NAN occurs in first entry. 
ri(isinf(ri))=ri(2); 
ri(isnan(ri))=ri(2);

idxri25G = find(ri>=0.25); %indices of ri values greater than 0.25
idxri25L = find(ri<=0.25); %indices of ri values less than 0.25

if isempty(idxri25L)
    pblri= 0; %if no ri values lower than 0.25, then PBL height is zero
else   
    if idxri25G(1)>idxri25L(1) %if ri starts below 0.25 then increases to above 0.25, idxri25G(1) is point right above 0.25
        upper = idxri25G(1);
        lower = idxri25G(1)-1;
        pblri = interp1(ri(lower:upper),hi(lower:upper),0.25,'linear'); 
    else 
        upper = idxri25L(1); %if ri starts above 0.25 then decreases to below 0.25, idxri25L(1) is point right above 0.25
        lower = idxri25L(1)-1;
        pblri = interp1(ri(lower:upper),hi(lower:upper),0.25,'linear');
    end
end

end

function [pblpt, dp] = pt_method(hi, pot)

[maxh,maxhidx] = max(hi);
pth = pot(10:maxhidx);
upH = hi(10:maxhidx);
topH = 3500;
height3k = upH(upH<=topH);
pt3k = pth(upH<=topH);
dp3k = gradient(pt3k,height3k); 
dp = gradient(pot,hi);
[maxdp,maxdpidx] = max(dp3k);
pblpt = height3k(maxdpidx);

end 

function [pblsh, dq] = sh_method(hi,rvv)

[maxh,maxhidx] = max(hi);
q = rvv./(1+rvv);
qh = q(10:maxhidx);
upH = hi(10:maxhidx);
topH = 3500;
height3k = upH(upH<=topH);
q3k = qh(upH<=topH);
dq3k = gradient(q3k,height3k);
dq = gradient(q,hi);
[mindq,mindqidx] = min(dq3k);
pblsh = height3k(mindqidx);

end

function [atmo] = layer_stability(hi, pot)

ds = 1;
du = 0.5;
m150 = find(hi >= 150);
start = m150(1);
diff = pot(start)-pot(1);

if diff < -ds
    atmo = "Convective Boundary Layer";
elseif diff > ds
    atmo = 'Stable Boundary Layer';
else
    atmo = 'Neutral Residual Layer';
end

end
