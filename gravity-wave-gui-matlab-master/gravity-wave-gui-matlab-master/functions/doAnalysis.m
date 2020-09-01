function [latitudeArray, longitudeArray, altNonFiltered, dataBlock, waveletTransform, clippedAlt, gWaveLocations, windSpeed] = doAnalysis(f, save, saveDir, showPowerSurfaces, lowerCutOffAltitude, upperCutOffAltitude, latitude, heightSamplingFrequency, printData)
% does g-wave analysis for a radiosonde sounding.
if nargin < 6
    upperCutOffAltitude = 40000; % flights never reach 40km.
end
if nargin < 5
    lowerCutOffAltitude = 12000;
end
if nargin < 4
    showPowerSurfaces = false;
end
if nargin < 3
    saveDirExists = false;
else
    saveDirExists = true;
end
if nargin < 2
    save = false;
end
if save
   [~, saveFileName, ~] = fileparts(f);
   % default save in same directory.
   saveFileName = strcat(saveFileName, '_gravity_wave_parameters.csv');
   % if a data directory is provided, use it.
   if saveDirExists
      saveFileName = fullfile(saveDir, saveFileName);
   end
end
data = readRadioSondeData(f);
[maxAlt, mai] = max(data.Alt);
[~, lai] = min(abs(data.Alt(1:mai) - lowerCutOffAltitude)); 
[~, mai] = min(abs(data.Alt(lai:mai) - upperCutOffAltitude));
mai = mai + lai;
if maxAlt < lowerCutOffAltitude && upperCutOffAltitude == 40000
    % filter data to altitude bounds
    fprintf("Flight %s did not reach %d m\n", f, lowerCutOffAltitude);
    latitudeArray = []; 
    longitudeArray = [];
    altNonFiltered = [];
    dataBlock = [];
    waveletTransform = [];
    clippedAlt = [];
    gWaveLocations = [];
    windSpeed = [];
    return
elseif upperCutOffAltitude ~= 40000 && data.Alt(mai) < (upperCutOffAltitude)
    fprintf("Flight %s did not reach %d m\n", f, upperCutOffAltitude);
    latitudeArray = []; 
    longitudeArray = [];
    altNonFiltered = [];
    dataBlock = [];
    waveletTransform = [];
    clippedAlt = [];
    gWaveLocations = [];
    windSpeed = [];
    return
elseif mai == lai + 1
    latitudeArray = []; 
    longitudeArray = [];
    altNonFiltered = [];
    dataBlock = [];
    waveletTransform = [];
    clippedAlt = [];
    gWaveLocations = [];
    windSpeed = [];
    return
end
mai = mai - 1;
% Prepare data

latitudeArray = data.Lat_( 1:mai);
longitudeArray = data.Long_(1:mai);
latitudeArray = latitudeArray(~isnan(latitudeArray));
longitudeArray = longitudeArray(~isnan(longitudeArray));
altNonFiltered = data.Alt(1:mai);
altNonFiltered = altNonFiltered(~isnan(altNonFiltered));

data = data(lai:mai, :);
data = rmmissing(data);
ws = data.Ws;
windSpeed = ws;
wd = data.Wd;
pressure = data.P;
alt = data.Alt;
temp = data.T;
time = data.Time;

u = -ws .* sind(wd); % from MetPy
v = -ws .* cosd(wd); % 

% heightSamplingFrequency = 5;
fprintf("height sampling frequency %d\n", heightSamplingFrequency);
[alt, u, v, temp, bvFreqSquared] = preprocessData(alt, u, v, temp, ...
    pressure, time, heightSamplingFrequency);
clippedAlt = alt;
% calculate constant values to use in analysis
coriolisFreq = coriolisFrequency(latitude);
% finally, do the wavelet transform.
wt = WaveletTransform(u, v, temp, heightSamplingFrequency);
waveletTransform = wt;
% get local maxima that (could) correspond to gravity wave packets
% "Peaks were identified as a function of scale and altitude" - MAL2014.

[rows, cols] = find(imregionalmax(wt.powerSurface, 8)); % 8 for 8-connectivity

subplot(1, 7, 1)
plot(wt.u_wind_component, alt, 'k')
%title("U wind component, eclipse launch 4", 'FontSize', 16)
%xlabel("windspeed (m/s)", 'fontsize', 14)
ylabel("altitude (m)", 'fontsize', 14)
subplot(1, 7, 2)
plot(abs(wt.uWavelet(100,:)), alt, 'k')
%title("U wavelet transform, eclipse launch 4", 'FontSize', 16)
%xlabel("wavelet power spectrum (m/s)", 'fontsize', 14)
%ylabel("altitude (m)", 'fontsize', 14)
subplot(1, 7, 3)
plot(abs(wt.uWavelet(200,:)), alt, 'k')
%title("U wavelet transform, eclipse launch 4", 'FontSize', 16)
%xlabel("wavelet power spectrum (m/s)", 'fontsize', 14)
%ylabel("altitude (m)", 'fontsize', 14)

subplot(1, 7, 4)
plot(abs(wt.uWavelet(300,:)), alt, 'k')
%title("U wavelet transform, eclipse launch 4", 'FontSize', 16)
%xlabel("wavelet power spectrum (m/s)", 'fontsize', 14)
%ylabel("altitude (m)", 'fontsize', 14)

subplot(1, 7, 5)
plot(abs(wt.uWavelet(400,:)), alt, 'k')
%title("U wavelet transform, eclipse launch 4", 'FontSize', 16)
%xlabel("wavelet power spectrum (m/s)", 'fontsize', 14)
%ylabel("altitude (m)", 'fontsize', 14)

subplot(1, 7, 6)
plot(abs(wt.uWavelet(500,:)), alt, 'k')
%title("U wavelet transform, eclipse launch 4", 'FontSize', 16)
%xlabel("wavelet power spectrum (m/s)", 'fontsize', 14)
%ylabel("altitude (m)", 'fontsize', 14)

subplot(1, 7, 7)
plot(abs(wt.uWavelet(600,:)), alt, 'k')
%title("U wavelet transform, eclipse launch 4", 'FontSize', 16)
%xlabel("wavelet power spectrum (m/s)", 'fontsize', 14)
%ylabel("altitude (m)", 'fontsize', 14)

if showPowerSurfaces
    f1 = figure;
    set(0, 'CurrentFigure', f1);
    colormap parula;
    imagesc(alt, wt.fourierWavelength, (wt.powerSurface));
    [~, titleName, ~] = fileparts(f);
    titleString = sprintf("%s", titleName);
    title(titleString, 'Interpreter', 'none');
    hold on;
    %plot(alt, wt.coi, 'k')
    %legend('cone of influence');
    %scatter(alt(cols), wt.fourierWavelength(rows), 'k*')
    ylabel('vertical wavelength (m)', 'FontSize', 14);
    xlabel('altitude (m)', 'FontSize', 14)
    c = colorbar('FontSize', 14);
    c.Label.String = 'power surface, (m^2/s^2)';
    %c.Label.Interpreter = 'latex';
    set(gca, 'YDir', 'normal');
    set(gca, 'YScale', 'log');
end
gWaveDetected = false;
first = true;
xValuesForPolygon = 1:size(wt.powerSurface, 2); % get n columns
yValuesForPolygon = wt.coi; % y values that we must check 
gWaveLocations = [];
for i=1:size(rows)
     % filter local maxima to COI.
     % create a polygon with the COI and query whether or not the x and y
     % values (cols(i) and waveletScales(i)) are within that polygon.
     if ~inpolygon(cols(i), wt.waveletScales(rows(i)), xValuesForPolygon, yValuesForPolygon)
         % if local maxima candidate is not inside COI polygon, skip it.
         continue;
     end
     % clip the wavelet transform to a box (s1, s2, a1, a2) that 
     % corresponds to where the power surface equals 1/4Smax
     [s1, s2, a1, a2] = wt.clipWindowedTransformToValue(rows(i), cols(i));
     if s1 == 0 || s2 == 0 || a1 == 0 || a2 == 0
         % Too close to an edge.
         continue
     end
     nCandidatesInsideWindow = 0;
     xCoordsOfWindow = [a1 a1 a2 a2];
     yCoordsOfWindow = [s2 s1 s1 s2];
     for k=1:size(rows)
         if inpolygon(cols(k), rows(k), xCoordsOfWindow, yCoordsOfWindow)
             nCandidatesInsideWindow = nCandidatesInsideWindow + 1;
         end
     end
     if nCandidatesInsideWindow > 1
         % to reconstruct wavelets within the closed contour...
         % get wavelet coefficients for all altitudes
         % and sum over the rows.
         continue;
     end 
     
     wwt = WindowedWaveletTransform(s1, s2, a1, a2); % helper object to ease passing parameters in to invertWaveletTransform
     % invert the wavelet transform in the windowed transform to get a wave
     % packet.
     % "Wavelet coefficients in the vicinity of the peak were used to
     % reconstruct temperature and wind perturbations associated with each
     % wave around the wave altitude ``z'' and to estimate the vertical
     % wavelength, lambda_z" - MAL2014.
     [ui, vi, tempi, lambda_z, horizWindVariance] = wt.invertWindowedTransform(wwt);
     % ^ u reconstructed, v reconstructed, temp reconstructed, vertical
     % wavenumber.
     % estimateParametersFromWavePacket thresholds wave candidates based on
     % criteria laid out in Murphy et al, 2014.
     [maxVal, ~] = max(horizWindVariance);
     fwhm = find(horizWindVariance >= 0.5*maxVal);
     ui = ui(fwhm);
     vi = vi(fwhm);
     tempi = tempi(fwhm);
     [~, ~, Q, theta, axialRatio, degreeOfPolarization] = estimateParametersFromWavePacket(ui, vi, tempi);
     if theta == 0
         % theta = 0 when wave packet does not pass filtering criteria.
        continue;
     end     
     % theta = azimuthFromUnitCircle(rad2deg(theta));
     theta = rad2deg(theta);
     % all equations below from Murphy et al, 2014:
     % "Radiosonde observations of gravity waves in the lower stratosphere
     %   over Davis, Antartica", table 2.
     intrinsicFreq = coriolisFreq*axialRatio;
     bvMean = mean(bvFreqSquared(a1:a2)); % Get the mean squared Brunt-Vaisala frequency over the height range of the gravity wave packet
     if ~((sqrt(bvMean) > intrinsicFreq) && (intrinsicFreq > coriolisFreq))
         % if the intrinsic frequency is greater than the buoyancy
         % frequency or if it's less than the coriolis frequency, the
         % gravity wave is not physical, so skip it.
         continue
     end
     if showPowerSurfaces
        set(0, 'CurrentFigure', f1);
        %scatter(alt(cols(i)), wt.fourierWavelength(rows(i)), 'k*');
     end
     gWaveDetected = true;
     %fprintf("m:%f\n", lambda_z);
     m = 2*pi / lambda_z; % vertical wavenumber (1 / meters)
     k_h = sqrt(((coriolisFreq^2*m^2)/(bvMean))*(intrinsicFreq^2/coriolisFreq^2 - 1)); % horizontal wavenumber (1 / meters)
     intrinsicVerticalGroupVel = -(1 / (intrinsicFreq*m))*(intrinsicFreq^2 - coriolisFreq^2); % m/s
     zonalWaveNumber = k_h*sin(theta);% 1/m
     meridionalWaveNumber = k_h*cos(theta); % 1 / m
     intrinsicVerticalPhaseSpeed = intrinsicFreq / m; % m/s
     intrinsicHorizPhaseSpeed = intrinsicFreq / k_h; % m/s
     intrinsicZonalGroupVel = zonalWaveNumber * bvMean / (intrinsicFreq * m^2); % m/s
     intrinsicMeridionalGroupVel = meridionalWaveNumber * bvMean / (intrinsicFreq * m^2); % m/s
     intrinsicHorizGroupVel = sqrt(intrinsicZonalGroupVel^2 + intrinsicMeridionalGroupVel^2); % m/s
     lambda_h = 2*pi / k_h; % horizontal wavelength (m)
     altitudeOfDetection = mean(alt(a1:a2)); % mean of the altitude range as the central altitude of the gravity wave.
     [~, detectionIndex] = min(abs(altNonFiltered - altitudeOfDetection));
     latitudeOfDetection = latitudeArray(detectionIndex);
     longitudeOfDetection = longitudeArray(detectionIndex);
     data = [altitudeOfDetection/1000, latitudeOfDetection, longitudeOfDetection, lambda_z/1000, lambda_h/1000, theta, axialRatio, intrinsicVerticalGroupVel, intrinsicHorizGroupVel, intrinsicVerticalPhaseSpeed, intrinsicHorizPhaseSpeed, degreeOfPolarization, Q];
     if first
         dataArray = data;
         gWaveLocations = [cols(i) rows(i)];
         first = false;
     else
         dataArray = [dataArray; data];
         gWaveLocations = [gWaveLocations; cols(i) rows(i)];
     end
     if printData 
        fprintf("Alt: %f, L_z: %f, L_h: %f, Theta (compass): %f, w/f: %f, period (hours): %f, Vert. group vel: %f, Horiz. group vel: %f, Vert. phase spd: %f, Horiz. phase spd: %f\n", altitudeOfDetection/1000, lambda_z/1000, lambda_h/1000, azimuthFromUnitCircle(theta), axialRatio, (2*pi/intrinsicFreq)/3600, intrinsicVerticalGroupVel, intrinsicHorizGroupVel, intrinsicVerticalPhaseSpeed, intrinsicHorizPhaseSpeed);
     end
end
if save && ~isfile(saveFileName) && gWaveDetected
         % check if the file exists - if it doesn't, write a header to
         % the file to ease further analysis.
         % writecell([header; num2cell(data)], saveFileName);
         % PROP DIR> azimunth from unti cirlc
         header = {'alt_of_detection_km' 'lat_of_detection' 'lon_of_detection' 'vert_wavelength_km' 'horiz_wavelength_km' 'propagation_dir' 'axial_ratio' 'int_vert_group_vel_ms' 'int_horiz_group_vel_ms' 'int_vert_phase_spd_ms' 'int_horiz_phase_spd_ms' 'degreeofpolarization' 'stokes_param_Q'};
         dataBlock = array2table(dataArray, 'VariableNames', header);
         writetable(dataBlock, saveFileName);
         
elseif save && isfile(saveFileName) && gWaveDetected
         % if the file does exist, append to it.
         % There is no overwrite functionality, so it's possible to run
         % the analysis multiple times and write duplicates to a file.
         % This must be taken care of in later analysis.
         dlmwrite(saveFileName, dataArray, 'delimiter', ',', '-append');
         header = {'alt_of_detection_km' 'lat_of_detection' 'lon_of_detection' 'vert_wavelength_km' 'horiz_wavelength_km' 'propagation_dir' 'axial_ratio' 'int_vert_group_vel_ms' 'int_horiz_group_vel_ms' 'int_vert_phase_spd_ms' 'int_horiz_phase_spd_ms' 'degreeofpolarization' 'stokes_param_Q'};
         dataBlock = array2table(dataArray, 'VariableNames', header);
end
if ~gWaveDetected
    fprintf("No gravity waves detected.\n");
    dataBlock = [];
elseif gWaveDetected
    header = {'alt_of_detection_km' 'lat_of_detection' 'lon_of_detection' 'vert_wavelength_km' 'horiz_wavelength_km' 'propagation_dir' 'axial_ratio' 'int_vert_group_vel_ms' 'int_horiz_group_vel_ms' 'int_vert_phase_spd_ms' 'int_horiz_phase_spd_ms' 'degreeofpolarization' 'stokes_param_Q'};
    dataBlock = array2table(dataArray, 'VariableNames', header);
end
end