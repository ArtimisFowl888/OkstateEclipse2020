function [N2] = bruntVaisalaFrequency(potentialTemperature, heightSamplingFrequency)
% Calculates BV frequency for a whole sounding, using
% N^2 = g/theta * dtheta / dz, where theta is potential temperature.
% Validate vertical profiles of bvfreq w/ papers
g = 9.8;
N2 = (g ./ potentialTemperature) .* gradient(potentialTemperature, heightSamplingFrequency); 
end