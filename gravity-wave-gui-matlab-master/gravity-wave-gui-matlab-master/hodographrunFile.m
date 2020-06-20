d = '/Users/thomascolligan/chile_data/renamed/bad_data_removed/all';
t = fullfile(d, "*.txt");
files = dir(t);
for i=1:size(files)
    current = files(i).name;
    current = fullfile(d, current);
    if ~contains(current, 'C12')
        continue
    end
    data = readRadioSondeData(current);
    [~, idx] = max(data.Alt);
    data = data(1:idx, :);
    data = data(data.Alt > 12000, :);
    if isempty(data)
        continue;
    end
    u = -data.Ws .* sind(data.Wd); % from MetPy
    v = -data.Ws .* cosd(data.Wd); %    
    subplot(2, 1, 1)
    [alt, u, v, temp, bvFreqSquared] = ... 
        preprocessDataNoResample(data.Alt, u, v, data.T, data.P, 5);
    while(true)
        subplot(1, 3, 1);
        plot(u, alt, 'b');
        subplot(1, 3, 2);
        plot(v, alt, 'b');
        sgtitle(files(i).name, 'Interpreter', 'none');
        [x, y] = ginput(2);
        [~, alt_1] = min(abs(alt - y(1)));
        [~, alt_2] = min(abs(alt - y(2)));
        %[~, alt_1] = min(abs(alt - 22.55*1000));
        %[~, alt_2] = min(abs(alt - 22.1*1000));
        upper = max(alt_1, alt_2);
        lower = min(alt_1, alt_2);
        subplot(1, 3, 3);
        plot(u(lower:upper), v(lower:upper));
        subplot(1, 3, 1)
        hold on;
        plot(u(lower), alt(lower), 'ro','MarkerSize', 14);
        plot(u(upper), alt(upper), 'ro', 'MarkerSize', 14);
        fprintf("%d, %d\n", alt(lower), alt(upper));
        subplot(1, 3, 3);
        hold on;
        plot(u(lower), v(lower), 'ro','MarkerSize', 14);
        % black is upper
        plot(u(upper), v(upper), 'ko', 'MarkerSize', 14);
        ellipse_save = 'Save hodograph data? Y/N [N]';
        str = input(ellipse_save, 's');
        if ~isempty(str)
            if strcmp(str, "n")
                subplot(1, 3, 3)
                cla
                continue
            end
            T = table(alt(lower:upper), u(lower:upper), v(lower:upper), temp(lower:upper), bvFreqSquared(lower:upper));
            T.Properties.VariableNames = {'alt' 'u' 'v' 'temp' 'bv2'};
            [~, n, ~] = fileparts(files(i).name);
            fname = sprintf("~/hodographs/%s-%d-%d.txt", n, alt(lower), alt(upper));
            writetable(T, fname);

        end
        prompt = 'Next file? Y/N [N]: ';
        str = input(prompt,'s');
        if ~isempty(str)
            if strcmp(str, "n")
                subplot(1, 3, 3)
                cla
                continue;
            else
                subplot(1, 3, 1)
                cla
                subplot(1, 3, 2)
                cla
                subplot(1, 3, 3)
                cla
                break
            end
        end
    end
end