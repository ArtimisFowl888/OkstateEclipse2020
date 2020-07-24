function [azimuth] = azimuthFromUnitCircle(theta)
%   Theta is in degrees. This function converts theta from degrees
%   counterclockwise from east to degrees clockwise from north.
%   Detailed explanation goes here
azimuth = 450 - theta;
if (azimuth > 360) 
    azimuth = azimuth - 360;
end
end

