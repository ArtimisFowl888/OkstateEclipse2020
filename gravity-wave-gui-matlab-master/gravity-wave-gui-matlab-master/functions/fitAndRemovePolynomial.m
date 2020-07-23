function [perturbationQuantity] = fitAndRemovePolynomial(time, data, order)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
%   look at varargin
if nargin < 3
    order = 2;
end
[p] = polyfit(time, data, order);
meanFlow = polyval(p, time);
perturbationQuantity = data - meanFlow;
end

