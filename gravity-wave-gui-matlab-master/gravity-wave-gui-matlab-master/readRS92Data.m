
function [data] = readRS92Data(filename, firstDataLine, numHeaderLines)
datainput = filename;
Sounding_data = RS92_import(datainput);

for i = 1:length(Sounding_data.GPSwinddir)
    Sounding_data.GPSwinddir(i) = strtok(Sounding_data.GPSwinddir(i),' ');
end

data.Alt = Sounding_data.GPSalt;
data.Ws = Sounding_data.GPSwindspeed;
data.Wd = str2double(Sounding_data.GPSwinddir);
data.T = Sounding_data.Temp;
data.P = Sounding_data.Pressure;
data  = struct2table(data);
end