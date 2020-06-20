function [data] = readGravityWaveParameters(dataDirectory)
% Reads all data files in dataDirectory.
t = fullfile(dataDirectory, "*.csv");
files = dir(t);
first = true;
for i=1:size(files)
    current = files(i).name;
    % fprintf("Current file: %s\n", current);
    current = fullfile(dataDirectory, current);
    if first
        data = readGravityWaveData(current); 
        first = false;
    else
        data = [data; readGravityWaveData(current)];
    end
end
end

