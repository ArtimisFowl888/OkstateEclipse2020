function [id1, id2] = findMinimaClosestToIndex(array, index)
%   Gets the two closest minima on either side of index in array.
%   Returns the indices into the array of the minima.
[~, locs] = findpeaks(-array); % find the maxima (the negative minima).
locs = sort(locs);
id2 = 0;
id1 = 0;
if size(locs, 1) == 1
    sz = size(locs, 2);
else
    sz = size(locs, 1);
end
for i=2:sz
    if (locs(i-1) < index) && (locs(i) > index)
        id1 = locs(i-1);
        id2 = locs(i);
    end
end
end

