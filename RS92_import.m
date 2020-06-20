function Sounding_data = RS92_import(filename, dataLines)
%  DIGITALSONDE2020060918ZH2514403PTU = IMPORTFILE(FILENAME) reads data
%  from text file FILENAME for the default selection.  Returns the data
%  as a table.

%  Sounding_data = RS92_import(FILE, DATALINES)
%  reads data for the specified row interval(s) of text file FILENAME.
%  Specify DATALINES as a positive scalar integer or a N-by-2 array of
%  positive scalar integers for dis-contiguous row intervals.

%  Example:
%  Sounding_data = RS92_import("E:\MATLAB Drive\Eclipse\digitalsonde2020060918Z_H2514403_ptu.csv", [1, Inf]);


%% Input handling

% If dataLines is not specified, define defaults
if nargin < 2
    dataLines = [1, Inf];
end

%% Setup the Import Options and import the data
opts = delimitedTextImportOptions("NumVariables", 7);

% Specify range and delimiter
opts.DataLines = dataLines;
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["Frame", "Pressure", "Temp", "Humidity", "GPSalt", "GPSwinddir", "GPSwindspeed"];
opts.VariableTypes = ["double", "double", "double", "double", "double", "double", "double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";

% Import the data
Sounding_data = readtable(filename, opts);

end