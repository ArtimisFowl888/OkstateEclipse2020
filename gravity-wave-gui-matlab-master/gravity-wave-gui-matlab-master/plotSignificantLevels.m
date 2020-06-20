function plotSignificantLevels(level, axes1, name, color)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
xs = xlim(axes1);
if size(level, 1) == 1 && size(level, 2) == 1
    ys = zeros(size(xs), 'like', xs) + level;
    line = plot(axes1, xs, ys, color, 'DisplayName', name);
    % legend(axes1, line, name)
else
for i=1:size(level)
    ys = zeros(size(xs), 'like', xs) + level(i);
    line = plot(axes1, xs, ys, color, 'DisplayName', name);
    % legend(axes1, line, name)
end
end    
end

