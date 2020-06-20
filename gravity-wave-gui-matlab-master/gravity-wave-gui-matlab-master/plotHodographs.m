d = '~/hodographs/';

t = fullfile(d, "*.txt");
files = dir(t); 
axs = [];
series_figure = figure;
hodo_fig = figure; offset = 10;
arrow_offset = 1 / 15;
counter = 1;
already_seen = [];
flight_num = [];
offsets = [];
coriolisFreq = coriolisFrequency(30.25);
unique_flights = ["F04","F07","F10","F11","F12","F13","F14","F16","F18","F19","F20","F21","F23","F24","F25"];
for k=1:size(unique_flights, 2)
    for i=1:size(files)
        flight_number = files(i).name(1:3);
        flight_number(1) = 'F';
    if strcmp(flight_number, unique_flights(k)) == 0
        %fprintf("%s %s\n", unique_flights(k), flight_number);
        continue;
    end
    % if str2num(flight_number(2:end)) ~= 23
    %     continue;
    % end
    data = readtable(fullfile(d, files(i).name));
    set(0, 'CurrentFigure', hodo_fig);
    ax = subplot(6, 5, i);
    axs = [axs;ax];
    eps = fit_ellipse(data.u, data.v, ax);
    hold on
    plot(data.u, data.v, 'k.')
    lambda_z = 2*(data.alt(end) - data.alt(1));
    m = 2*pi / lambda_z;
    p = eps.phi;
    rot = [cos(p) -sin(p); sin(p) cos(p)];
    uv = [data.u data.v];
    uvrot = rot*uv';
    urot = uvrot(1, :);
    dT = data.temp(2:end) - data.temp(1:end-1);
    dz = data.alt(2:end) - data.alt(1:end-1);
    wf = eps.long_axis / eps.short_axis;
    bvMean = mean(data.bv2);
    intrinsicFreq = coriolisFreq*wf;
    %fprintf("%0.10f, %0.10f ", (coriolisFreq^2 * m^2)/abs(bvMean), wf^2 - 1);
    k_h = sqrt((coriolisFreq^2*m^2)/(abs(bvMean))*(wf^2 - 1)); % horizontal wavenumber (1 / meters)
    %fprintf("%f %f\n", intrinsicFreq, wf);
    intrinsicHorizPhaseSpeed = intrinsicFreq / k_h; % m/s
    fprintf("m:%f, lz:%f, h:%f,, bv:%f\n", m, lambda_z, intrinsicHorizPhaseSpeed, bvMean);
    k_h_2 = sqrt((intrinsicFreq^2 - coriolisFreq^2 )* (m^2 / abs(bvMean)));
    int2 = intrinsicFreq/k_h_2;
    % fprintf("m:%f, lz:%f, h:%f, kh:%f\n", m, lambda_z, intrinsicHorizPhaseSpeed, int2);
    dTdz = dT./dz;
    eta = mean(dTdz.*urot(1:end-1));
    if eta < 0
        p = p - pi;
    end
    str = sprintf("f: %s, ^{w}/{f}=%0.1f, t=%0.1f, m_z=%0.1f", ...
        files(i).name(1:3), wf, azimuthFromUnitCircle(rad2deg(p)),...
        lambda_z/1000);
    %title(str);
    fprintf("%s\n", str);
    set(0, 'CurrentFigure', series_figure);
    xlim([5, 155]);
    ylim([12, 33]);
    alt_of_detection_km = mean(data.alt) / 1000;
    x1 = counter*offset;
    x2 = counter*offset + wf*cosd(rad2deg(p));
    y1 = alt_of_detection_km;
    y2 = alt_of_detection_km + wf*sind(rad2deg(p));
    hold on;
    p1 = [x1 y1];
    p2 = [x2 y2];
    dp = p2-p1;
    %quiver(p1(1),p1(2),dp(1),dp(2), 'AutoScale', 'on', 'color','#9a0200', 'linewidth', 2);
    [xf, yf] = ds2nfu([x1 x2], [y1 y2]);
    annotation(gcf, 'arrow', xf,yf, 'color', '#9a0200', 'LineWidth', 2)
    if strcmp(flight_number, "F23")
        if alt_of_detection_km > 20 && alt_of_detection_km < 24
            xc = [xf(1) - 0.125, xf(2)-0.02];
            yc = [yf(1) + 0.1, yf(1)+0.05];
            annotation(gcf, 'textarrow', xc, yc, 'String', 'Eclipse Wave #2')
        elseif alt_of_detection_km > 20
            xc = [xf(1) - 0.125, xf(2)- 0.02];
            yc = [yf(1) + 0.1, yf(1)+0.05];
            annotation(gcf, 'textarrow', xc, yc, 'String', 'Eclipse Wave #3')
        end
        fprintf("%f\n", alt_of_detection_km);
    end
    %plot([x1 x2], [y1 y2], 'color', '#9a0200', 'linewidth', 3);
    placeholder = [counter*offset counter*offset];
    plot(placeholder, [12, 32.5], 'k'); % plot altitude in km.
    end
    offsets = [offsets, counter*offset];
    counter = counter + 1;
end
% 10 -> 150

linkaxes(axs, 'xy');
set(0, 'CurrentFigure', hodo_fig);
sgtitle("All hodographs for the radiosonde campaign")
set(0, 'CurrentFigure', series_figure);
% %offsets = offsets(1:end-1);
flight_num = flight_num(1:end-1, :);
xticks(offsets);
xticklabels(unique_flights); 
set(gca,'XTickLabelRotation', 45, 'fontsize', 16)
ylabel("Altitude of detection (km)") 
xlabel("Flight number")
title("Propagation direction and detection altitude of gravity waves (hodograph method)", 'fontsize', 16);
