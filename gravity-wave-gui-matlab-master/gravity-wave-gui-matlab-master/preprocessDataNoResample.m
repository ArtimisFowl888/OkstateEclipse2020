function [alt, u, v, temp, bvFreqSquared] = preprocessDataNoResample(alt, u, v, temp, pressure, heightSamplingFrequency)
% This function resamples the data and removes the background.
potentialTemperature = (1000.0^0.286)*temp./(pressure.^0.286); % from Jaxen
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

