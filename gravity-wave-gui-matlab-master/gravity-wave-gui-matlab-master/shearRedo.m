function [HLS] = shear(fullfilename,ax_1)

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
levelsX = false(length(ws),1);
levelsY = false(length(ws),1);

for k = 1:length(ws) 
    if LMX(k) == 1 %each local max is assessed
        stpidx = find(height >= height(k)+1000,1); %find index of height 1000 meters above local max height
        if ~isempty(stpidx) % stpidx will be an empty array when height of local max + 1000 m is larger than burst height
            if length(height)>stpidx % avoid looking at maximums that are within 1000 meters of burst height
                wl = min(ws(k:stpidx)); % find minumum wind speed between local max height and 1000 m above
                if ws(k)-wl >= 7.5 %difference must me greater than 7.5 to be considered significant shear
                    levelsX(k) = true; %set logical value to true at the height index
                end
            end
        end
    end
end


for j = 1:length(ws)
    if LMN(j) == 1 %each local max is assessed
        stpidxY = find(height >= height(j)+1000,1); %find index of height 1000 meters above local max height
        if ~isempty(stpidxY) % stpidx will be an empty array when height of local max + 1000 m is larger than burst height
            if length(height)>stpidxY % avoid looking at maximums that are within 1000 meters of burst height
                wg = max(ws(j:stpidxY)); % find minumum wind speed between local max height and 1000 m above
                if wg-ws(j) >= 7.5 %difference must me greater than 7.5 to be considered significant shear
                    levelsY(j) = true; %set logical value to true at the height index
                end
            end
        end
    end
end


HLX = height(levelsX); % use logical array to determine heights of significant wind shear
HLY = height(levelsY);

HLS = sort([HLX;HLY]);

if isempty(ax_1) % Allows this code to be used without the GUI, do not get rid of
    f1 = figure(); 
    ax_1 = axes(f1);
end 
plot(ax_1, ws, height,'DisplayName','Wind Speed')
hold(ax_1, 'on');
plot(ax_1, ws(LMX), height(LMX),'r*', 'DisplayName', 'Local Maximums')
plot(ax_1, ws(LMN), height(LMN),'b*', 'DisplayName', 'Local Minimums');
for i = 1:length(HLX)
    yline(ax_1, HLX(i), 'DisplayName', num2str(HLX(i)));
end
for i = 1:length(HLY)
    yline(ax_1,HLY(i),'b', 'DisplayName', num2str(HLY(i)));
end
title(ax_1,'Height (m) vs Wind Speed (m/s)')
ylabel(ax_1,'Height (m)')
xlabel(ax_1, 'Wind Speed (m/s)')
legend(ax_1);


end
    
