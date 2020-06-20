function [HL] = shear(fullfilename,ax_1)

%This code requires readSondFile.m to be in the current working directory
%
%INPUTS: 1. Full path to the data file 
%        2. GUI plot name (Use [] in this field when running in Command
%           Window without the GUI)
%
%OUTPUTS: 1. Array of significant shear levels in meters
%
%
%This code finds levels of signifanct wind shear. It finds the local
%wind speed maxima and for each maxima scans between that level and 1000
%meters above for a minimum wind speed. It then takes the difference
%between the max and min. If the difference is greater than or egual to
%7.5 m/s, the max level is recorded as a level of significant wind shear. 
%
% This code can be used with the collaporativeApp.mlapp GUI


%get data from profile data file
data = readSondeFile(fullfilename);
w = data.Ws; %wind Speed in m/s
alt = data.Alt; %altitude (MSL) in m

% Cut out data that was obtained after burst
[maxa,maxaidx] = max(alt);
ws = w(1:maxaidx);
height = alt(1:maxaidx)-alt(1);

%find local max 
LMX = islocalmax(ws);
LMN = islocalmin(ws);
%initialize logical array
levels = false(length(ws),1);

for k = 1:length(ws) 
    if LMX(k) == 1 %each local max is assessed
        stpidx = find(height >= height(k)+1000,1); %find index of height 1000 meters above local max height
        if ~isempty(stpidx) % stpidx will be an empty array when height of local max + 1000 m is larger than burst height
            if length(height)>stpidx % avoid looking at maximums that are within 1000 meters of burst height
                wl = min(ws(k:stpidx)); % find minumum wind speed between local max height and 1000 m above
                if ws(k)-wl >= 7.5 %difference must me greater than 7.5 to be considered significant shear
                    levels(k) = true; %set logical value to true at the height index
                end
            end
        end
    end
end

HL = height(levels); % use logical array to determine heights of significant wind shear

if isempty(ax_1) % Allows this code to be used without the GUI, do not get rid of
    f1 = figure(); 
    ax_1 = axes(f1);
end
% Clears plot after loading a new file in the GUI
plot(ax_1, ws, height, 'DisplayName', 'wind speed')
hold(ax_1, 'on');
plot(ax_1, ws(LMX), height(LMX),'r*', 'DisplayName', 'local max')
plot(ax_1, ws(LMN), height(LMN),'b*', 'DisplayName', 'local min');

for i = 1:length(HL)
    yline(ax_1, HL(i), 'DisplayName', num2str(HL(i))); %Plot all of the significant shear levels
end

hold(ax_1, 'off');
title(ax_1,'Height (m) vs Wind Speed (m/s)')
ylabel(ax_1,'Height (m)')
xlabel(ax_1, 'Wind Speed (m/s)')
legend(ax_1);
end
    
