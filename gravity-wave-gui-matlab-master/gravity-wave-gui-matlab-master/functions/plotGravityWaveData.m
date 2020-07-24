function plotGravityWaveData(data, altitudeArray, ...
    waveletTransform, gWaveLocations, clippedAlt, axes1, axes2)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

    placeholder = zeros(size(altitudeArray), 'like', altitudeArray);
    plot(axes2, placeholder, altitudeArray/1000, 'k'); % plot altitude in km.
    hold(axes2, 'on');
    % The magnitudes of the red lines are the axial ratios of the
    % gravity waves - axial ratio = intrinsic frequency / coriolis
    % frequency.
    % The for loop below just plots the red lines in the direction of
    % propagation of the gravity wave
    offset = 0;
    if ~isempty(data)
        for q=1:size(data.alt_of_detection_km)
            x1 = offset;
            magnitude = data.axial_ratio(q);
            angle = data.propagation_dir(q);
            x2 = offset + magnitude*cosd(angle);
            y1 = data.alt_of_detection_km(q);
            y2 = data.alt_of_detection_km(q) + magnitude*sind(angle);
            plot(axes2, [x1 x2], [y1 y2], 'r', 'DisplayName', 'g-wave');
        end
    end
    xlim(axes2, [-5 5]);
    title(axes2, "Gravity wave altitude of detection and propagation direction", 'FontSize', 8);
    ylabel(axes2, 'Altitude (km)');
    set(axes1, 'XTickMode', 'auto', 'XTickLabelMode', 'auto');
    set(axes1, 'YTickMode', 'auto', 'YTickLabelMode', 'auto');
    %set(app.UIAxes_2, 'XTickMode', 'auto', 'XTickLabelMode', 'auto');
    set(axes2, 'YTickMode', 'auto', 'YTickLabelMode', 'auto'); 
    if ~isempty(waveletTransform)
        imagesc(axes1, clippedAlt, waveletTransform.fourierWavelength, log10(waveletTransform.powerSurface));
        hold(axes1, 'on');
        plot(axes1, clippedAlt, waveletTransform.coi, 'k');
    end
    if ~isempty(data) && ~isempty(gWaveLocations)
        s = scatter(axes1, clippedAlt(gWaveLocations(:, 1)), waveletTransform.fourierWavelength(gWaveLocations(:, 2)), 'ro');
        legend(axes1, s, 'gravity wave');
    end
    if ~isempty(waveletTransform)
        ylim(axes1, [waveletTransform.s0 Inf]);
        ylabel(axes1, 'Wavelength (m)');
        xlabel(axes1, 'Altitude (m)');
    end

end

