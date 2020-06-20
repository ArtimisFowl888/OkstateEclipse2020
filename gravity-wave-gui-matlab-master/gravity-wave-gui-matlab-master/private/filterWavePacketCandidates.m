function [goodMaximaRows, goodMaximaCols] = filterWavePacketCandidates(waveletTransform, localMaximaRows, localMaximaCols)
%filterWavePacketCandidates Filters wave packet candidates by calculating the Stokes
%parameters and degree of polarization. If Q < 0.05 || P < 0.05, the
%candidate is discarded. If d < 0.5 | d > 1, the candidate is also
%discarded. Otherwise, the file name, bounding box (s1, s2, z1, z2), the
%position of the local max, and the parameters are stored.

goodMaximaRows = zeros('like', localMaximaRows);
goodMaximaCols = zeros('like', localMaximaCols);
k = 0;
for i=1:size(localMaximaRows, 1)
    % first, clip the local maxima to 1/4Smax.
    currentMaxRow = localMaximaRows(i);
    currentMaxCol = localMaximaCols(i);
    %windowedWaveletTransform = extractWindowAroundLocalMax(waveletTransform.powerSurface, currentMaxCol, currentMaxRow);
    [row_index_1, row_index_2, col_index_1, col_index_2] = waveletTransform.clipWindowedTransformToValue(currentMaxRow, currentMaxCol);
    if row_index_1 == 0 || row_index_2 == 0 || col_index_1 == 0 || col_index_2 == 0
       %fprintf("Maxima too close to power surface edge. Most likely noise anyway.\n");
       continue;
    end
    oneQuarterMaxWindow = WindowedWaveletTransform(row_index_1, row_index_2, col_index_1, col_index_2);
    [u, v, temp, ~] = waveletTransform.invertWindowedTransform(oneQuarterMaxWindow);
    [theta, axialRatio, degreeOfPolarization] = estimateParametersFromWavePacket(u, v, temp);
    if theta == 0 || axialRatio == 0 || degreeOfPolarization == 0
        %fprintf("Wave packet did not satisfy critera\n");
        continue;
    end
    k = k + 1;
    goodMaximaRows(k) = currentMaxRow;
    goodMaximaCols(k) = currentMaxCol;
end
goodMaximaRows = goodMaximaRows(1:k);
goodMaximaCols = goodMaximaCols(1:k);
end
