function [averagedArray, averagedAlt] = averageToAltitudeResolution(array, altitude, resolution)
%UNTITLED Summary of this function goes here
%   Averages a time series of data to a given altitude resolution. Steps:
%   walk through the altitude array, keeping a running sum of the values in
%   "array" at the same indices. When altBegin - altEnd > resolution,
%   divide the sum by the number of indices between altBegin and altEnd,
%   and store it in a new array - averagedArray.

averagedArray = zeros('like', array);
averagedAlt = zeros('like', altitude);
altBegin = altitude(1);
altEnd = altitude(1);
k = 0;
s = 0;
nPoints = 0;
for i=1:size(altitude, 1)
    altEnd = altitude(i);
    s = s + array(i);
    nPoints = nPoints + 1;
    if (altEnd - altBegin) >= resolution
        k = k + 1;
        averagedArray(k) = s / nPoints;
        averagedAlt(k) = altBegin + (altEnd - altBegin) / 2;
        s = 0;
        altBegin = altEnd;
        nPoints = 0;
    end
end
averagedArray = averagedArray(1:k);
averagedAlt = averagedAlt(1:k);
end

