d = '~/stokes-params/before_eclipse';
all = readGravityWaveParameters(d);

% theta is in unit circle angle here.
% size(before)
% size(after)
% before = before(before.axial_ratio > 20, :);
% before = removevars(before, {'int_vert_group_vel_ms', 'int_horiz_group_vel_ms', 'degreeofpolarization', 'lon_of_detection', 'lat_of_detection'});
% after = removevars(after, {'int_vert_group_vel_ms', 'int_horiz_group_vel_ms', 'degreeofpolarization', 'lon_of_detection', 'lat_of_detection'});
% after = after(after.axial_ratio > 20, :);