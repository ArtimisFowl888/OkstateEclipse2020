function [data] = readRadioSondeData(filename, firstDataLine, numHeaderLines)
%UNTITLED2 Reads radiosonde data. 
%   Detailed explanation goes here
if nargin < 2
    firstDataLine = 21;
    numHeaderLines = 18;
end
opts = detectImportOptions(filename, 'NumHeaderLines', numHeaderLines);
opts.DataLines = [firstDataLine Inf];
data = readtable(filename, opts);
end

