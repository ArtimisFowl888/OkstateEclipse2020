function [intrinsicHorizPhaseSpeed, lambda_h] = calcParams(lambda_z, axialRatio, theta, bvFreqSquared)
%CALCPARAMS This function calculates g-wave parameters from 
% hodograph data.
latitude = -30.250; % Latitude of launch location.
coriolisFreq = coriolisFrequency(latitude);
intrinsicFreq = coriolisFreq*axialRatio;
fprintf("%f %f\n", axialRatio, 2*pi/(intrinsicFreq*3600));
bvMean = abs(mean(bvFreqSquared)); % Get the mean squared Brunt-Vaisala frequency over the height range of the gravity wave packet
m = 2*pi / lambda_z; % vertical wavelength (1 / meters)
k_h = sqrt(((coriolisFreq^2*m^2)/(bvMean))*(intrinsicFreq^2/coriolisFreq^2 - 1)); % horizontal wavenumber (1 / meters)
%intrinsicVerticalGroupVel = -(1 / (intrinsicFreq*m))*(intrinsicFreq^2 - coriolisFreq^2); % m/s
zonalWaveNumber = k_h*sin(theta);% 1/m
meridionalWaveNumber = k_h*cos(theta); % 1 / m
%intrinsicVerticalPhaseSpeed = intrinsicFreq / m; % m/s
intrinsicHorizPhaseSpeed = intrinsicFreq / k_h; % m/s
intrinsicZonalGroupVel = zonalWaveNumber * bvMean / (intrinsicFreq * m^2); % m/s
intrinsicMeridionalGroupVel = meridionalWaveNumber * bvMean / (intrinsicFreq * m^2); % m/s
%intrinsicHorizGroupVel = sqrt(intrinsicZonalGroupVel^2 + intrinsicMeridionalGroupVel^2); % m/s
lambda_h = 2*pi / k_h; % horizontal wavelength (m)


end

