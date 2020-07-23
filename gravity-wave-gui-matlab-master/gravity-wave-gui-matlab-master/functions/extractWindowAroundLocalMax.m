function [windowedWaveletTransform] = extractWindowAroundLocalMax(powerSurface, localMaxCol, localMaxRow)
% Returns a custom object that makes inverting the wavelet power surface easier.
ofs = 99;
n_rows = size(powerSurface, 1);
n_cols = size(powerSurface, 2);

first_row = localMaxRow - ofs;
last_row = localMaxRow + ofs;
first_col = localMaxCol - ofs;
last_col = localMaxCol + ofs;
if first_row < 1
   first_row = 1;
end
if last_row > n_rows
   last_row = n_rows;
end
if last_col > n_cols
   last_col = n_cols;
end
if first_col < 1
   first_col = 1;
end
windowedWaveletTransform = WindowedWaveletTransform(first_row, last_row, first_col, last_col);
end

