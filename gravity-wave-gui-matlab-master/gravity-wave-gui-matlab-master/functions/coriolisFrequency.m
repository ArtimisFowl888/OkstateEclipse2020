function [f] = coriolisFrequency(latitude)
%coriolisFrequency Calculate Coriolis frequency at latitude.
%   Detailed explanation goes here
f = 2*7.2921e-5*sind(latitude);
end

