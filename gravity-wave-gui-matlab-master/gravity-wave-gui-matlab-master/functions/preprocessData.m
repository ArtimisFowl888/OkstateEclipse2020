function [alt, u, v, temp, bvFreqSquared] = preprocessData(alt, u, v, temp, pressure, time, heightSamplingFrequency)
% This function resamples the data and removes the background.
alt = seconds(alt);
potentialTemperature = (1000.0^0.286)*temp./(pressure.^0.286); % from Jaxen
tt = timetable(alt, u, v, temp, potentialTemperature, time);
uiq = unique(tt.alt);
tt = retime(tt, uiq);
% tt = retime(tt, 'secondly', 'linear'); % interpolate to regular grid
dt = seconds(heightSamplingFrequency);
tt = retime(tt, 'regular', 'linear', 'TimeStep', dt);
% using linear interpolation.
alt = seconds(tt.alt);
u = tt.u';
v = tt.v';
temp = tt.temp';
time = tt.time';
potentialTemperature = tt.potentialTemperature;
% remove background winds with a moving mean.
altExtent = max(alt) - min(alt);
np = max(fix(altExtent/heightSamplingFrequency/4),  11);
% enforce uniform spatial sampling...
% u = averageToAltitudeResolution(u, alt, heightSamplingFrequency);
% v = averageToAltitudeResolution(v, alt, heightSamplingFrequency);
% temp = averageToAltitudeResolution(temp, alt, heightSamplingFrequency);
% potentialTemperature = averageToAltitudeResolution(potentialTemperature, alt, heightSamplingFrequency);
% alt = averageToAltitudeResolution(alt, alt, heightSamplingFrequency);
bvFreqSquared = bruntVaisalaFrequency(potentialTemperature, heightSamplingFrequency); % returns the squared BV frequency.
meanU = movmean(u, np);
meanV = movmean(v, np);
meanT = movmean(temp, np);
u = u - meanU;
v = v - meanV;
temp = temp - meanT;
end

