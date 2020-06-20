
n_points = 600;
u = zeros(1, n_points);
v = zeros(1, n_points);
alt = 1:n_points;
alt = alt * 50;

window = alt(200:450);
m_z = 2*pi / 5000; % vertical wavelength is 5km.
a = 1:size(window, 2);
envelope = exp(-(a - 125).^2/(12500));
temp = u;
u(100:350) = gaussian_cosine;
v(100:350) = gaussian_sin;
plot(u, alt)
wt = WaveletTransform(u, v, temp, 50);
contourf(alt, wt.fourierWavelength, wt.powerSurface);
[rows, cols] = find(imregionalmax(wt.powerSurface));
hold on;
plot(alt, wt.coi, 'k')
scatter(alt(cols), wt.fourierWavelength(rows), 'ro');

xValuesForPolygon = 1:size(wt.powerSurface, 2); % get n columns
yValuesForPolygon = wt.coi; % y values that we must check 
for i=1:size(rows, 1)
     % filter local maxima to COI.
     % create a polygon with the COI and query whether or not the x and y
     % values (cols(i) and waveletScales(i)) are within that polygon. This
     % function seems to work.
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
         % I should probably figure out how to visualize this.
         continue;
     end
     wwt = WindowedWaveletTransform(s1, s2, a1, a2); % helper object to ease passing parameters in to invertWaveletTransform
     % invert the wavelet transform in the windowed transform to get a wave
     % packet.
     % "Wavelet coefficients in the vicinity of the peak were used to
     % reconstruct temperature and wind perturbations associated with each
     % wave around the wave altitude ``z'' and to estimate the vertical
     % wavelength, lambda_z" - MAL2014.
     [ui, vi, tempi, lambda_z] = wt.invertWindowedTransform(wwt);
     
     % estimateParametersFromWavePacket thresholds wave candidates based on
     % criteria laid out in Murphy et al, 2014.
     [~, ~, Q, theta, axialRatio, degreeOfPolarization] = estimateParametersFromWavePacket(ui, vi, tempi);
     if theta == 0
         % theta = 0 when wave packet does not pass filtering criteria.
        continue;
     end
    
end









