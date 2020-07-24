function [dataTimetable, metadataText] = readSondeFile(filename)
%readSondeFile Reads radiosonde txt data file 
%  
% Returns dataTable and metadataText
% 
% dataTable is a table with columns/variables from data file. 
% Column names will be coverted to valid MATLAB variable names, for example:
% Time P T Hu Ws Wd Long_ Lat_ Alt Geopot Dewp_ Virt_Temp Rs D
%  
% Optional output argument metadataText consists of the plain text header
% and footer lines in the data file.
% 
% Example usage:
%  [traj, metadata] = readSondeFile('08212017C8_Center_Blaunch_Acer_181604.txt');
%

% 2019/05/29 v1.0 AU


%% Sounding file format, example txt file

% Flight Information:     	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Launch Date:            	                       	Monday, August 21, 2017	   	                   	Launch Time:    	           	6:16:04 PM   	     	End of Ascent:	     	           	1:26:53 AM	        
% Station name:           	                       	                       	   	                   	Number of sonde:	           	00627813     	     	              	     	           	          	        
% Ground values:          	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Pressure:               	                       	864.2 hPa              	   	                   	Temperature:    	           	22.9 °C      	     	Humidity:     	     	           	31 %      	        
% Wind Direction:         	                       	0 °                    	   	                   	Wind Speed:     	           	5 m/s        	     	Cloud group:  	     	           	9////     	        
% Position:               	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Longitude:              	                       	-104.454 °             	   	                   	Latitude:       	           	42.277 °     	     	Altitude:     	     	           	1389 m    	        
% Staff:                  	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Company:                	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Operator:               	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Events:                 	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Highest Point:          	                       	8.8 hPa                	   	                   	32378 m         	           	             	     	              	     	           	          	        
% Tropopauses:            	                       	1.: 119.4 hPa          	   	                   	                	           	             	     	              	     	           	          	        
% Max Winds:              	                       	1.: 167.0 hPa          	   	                   	                	           	             	     	              	     	           	          	        
% Remarks:                	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
%                         	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Profile Data:           	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% Time                    	P                      	T                      	Hu 	Ws                 	Wd              	Long.      	Lat.         	Alt  	Geopot        	Dewp.	Virt. Temp 	Rs        	D       
% [sec]                   	[hPa]                  	[°C]                   	[%]	[m/s]              	[°]             	[°]        	[°]          	[m]  	[m]           	[°C] 	[°C]       	[m/s]     	[kg/m3] 
% 0                       	864.2                  	22.9                   	31 	4.5                	000             	-104.453800	42.277000    	1389 	1389          	4.9  	24.0       	0.0       	1.017109
% 1                       	863.5                  	22.9                   	31 	4.6                	360             	-104.453817	42.276938    	1396 	1396          	4.9  	24.0       	6.7       	1.016504
% 2                       	862.9                  	22.8                   	31 	4.7                	001             	-104.453835	42.276877    	1402 	1402          	4.9  	23.9       	6.7       	1.015900
% ...
% 5189                    	9.0                    	-39.3                  	3  	11.1               	087             	-103.962896	42.324328    	32373	32199         	-67.0	-39.3      	7.3       	0.013422
% 5190                    	9.0                    	-39.3                  	3  	11.1               	087             	-103.962989	42.324310    	32380	32207         	-67.0	-39.3      	7.3       	0.013407
% Tropopauses:            	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% 1. Tropopause: 119 [hPa]	                       	                       	   	2. Tropopause: ----	                	           	             	     	              	     	           	          	        
% LCL: 661.2 [hPa]        	                       	                       	   	LI: 3              	                	           	K-Index: 19  	     	              	     	           	          	        
% LFC: -                  	                       	                       	   	SI: 3              	                	           	S-Index: 29  	     	              	     	           	          	        
% CCL: 576.2 [hPa]        	                       	                       	   	CAPE: -            	                	           	TT-Index: 44 	     	              	     	           	          	        
% EL: -                   	                       	                       	   	CINH: -            	                	           	Ko-Index: -25	     	              	     	           	          	        
% Reason of Stop Sounding:	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% TU                      	Terminated by User (TU)	                       	   	                   	                	           	             	     	              	     	           	          	        
%                         	                       	                       	   	                   	                	-          	             	     	              	     	           	          	        
% Page 1 of 1             	                       	                       	   	                   	                	           	             	     	              	     	           	          	        
% 

%% Specify file format parameters specific to radiosonde txt data files
% Number of lines in the header section (before data table)
numHeaderLines = 18;

% Number of lines in the footer section (after data table)
% Note that last line in footer/file is empty
numFooterLines = 11;

% Line number where table data starts (after table column names and units)
firstDataLine = 21;

% Line number with units
unitsLine = firstDataLine - 1;

%% Import table
% Column names will be coverted to valid MATLAB variable names
% (for example the column Lat. will be imported as Lat_)
opts = detectImportOptions(filename, 'NumHeaderLines', numHeaderLines);

% Table data starts at firstDataLine, but last line can very from file to file
% Note that footer lines will be processed as NaN values
% (10 footer lines + 1 empty line will be interpreted as 10 rows of NaN
% values for each column.
opts.DataLines = [firstDataLine Inf];
opts.VariableUnitsLine = unitsLine;
dataTable = readtable(filename, opts);

%% Import file metadata text (header + footer)
text = fileread(filename);

% Split text character array into individual text lines
% Sounding txt data file is using CR+LF as end of line characters
lines = strsplit(text,'\r\n')';

% Return header and footer lines as metadata text
% Note that last line in file is empty 
metadataText = strjoin(lines([1:numHeaderLines end-numFooterLines+1:end]), '\r\n');

%% Check that number of rows with NaN values is consistent with number of lines in the file footer

% Table of logical values corresponding to a value being NaN or not.
nanvalues = ismissing(dataTable);

% Number of rows with all columns having NaN value
numNaNDataRows = nnz(all(nanvalues,2));

% If inconsitent, throw a warning and leave table as is for inspection
% Otherwise, assume processing was correct and discard the last rows with 
% NaN values which correspond to the footer lines.
if numNaNDataRows ~= numFooterLines - 1
    warning('Number of footer lines not as expected or some data rows are invalid. Inspect data file and function outputs for validity.');
else
    dataTable(end-numFooterLines+1:end,:) = [];
end

% Create data timetable
dataTimetable = table2timetable(dataTable(:,2:end), 'RowTimes', seconds(dataTable.Time));
end

