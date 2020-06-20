function [outFileList, waveletTransforms] = plotTimeSeriesProfiles(fileList, path, lowerCutOffAltitude, ...
    upperCutOffAltitude, axes2)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
save = false;
showPowerSurfaces = false;
first = true;
saveDirectory = 'gravityWaveData';
counter = 0;
for i=1:size(fileList, 2)
    try
        current = fileList(i);
        current = current{1};
        current = fullfile(path, current);
        [~, ~, alt, dat, waveletTransform, clippedAlt, ~, ~] = doAnalysis(current, save, saveDirectory, ...
            showPowerSurfaces, lowerCutOffAltitude*1000, upperCutOffAltitude*1000);
        if isempty(dat)
            continue;
        end
        offset = 15;
        placeholder = zeros(size(alt), 'like', alt) + (counter*offset);
        plot(axes2, placeholder, alt/1000, 'k'); % plot altitude in km.
        angle = dat.propagation_dir;
        magnitudes = dat.axial_ratio;
        for q=1:size(dat.alt_of_detection_km)
            x1 = counter*offset;
            x2 = counter*offset + magnitudes(q)*cosd(angle(q));
            y1 = dat.alt_of_detection_km(q);
            y2 = dat.alt_of_detection_km(q) + magnitudes(q)*sind(angle(q));
            plot(axes2, [x1 x2], [y1 y2], 'r');   
        end
        waveletTransform.alt = clippedAlt;

        if first
            indicesForFilenames = i;
            offsets = counter*offset;
            wavelets = waveletTransform;
            % contourf(axes1, clippedAlt, waveletTransform.fourierWavelength, waveletTransform.powerSurface);
            first = false;
        else
            indicesForFilenames = cat(2, indicesForFilenames, i);
            offsets = cat(2, offsets, counter*offset);
            wavelets = cat(2, wavelets, waveletTransform);
            
        end
        counter = counter + 1;
    catch e
        if (strcmp(e.identifier, 'MATLAB:table:UnrecognizedVarName'))
            fprintf("Data file %s does not contain a variable needed for analysis. Rerun sounding.\n", files(i).name);
            fprintf("----------------------------\n");
            continue;
        end
        rethrow(e);
    end
        fprintf("----------------------------\n");
end

xticks(axes2, offsets);
filenames = fileList(indicesForFilenames);
outFileList = filenames;
waveletTransforms = wavelets;
xticklabels(axes2, filenames);
yticks(axes2, 'auto');
set(axes2, 'XTickLabelRotation', 45);
ylabel(axes2, "Altitude (km)")
xlabel(axes2, "Launch")
end

