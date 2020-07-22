d = 'C:\Users\Level1Zach\Desktop\testdata';

sonde = 1;
% if using DFM-17 set sonde = 1
% if using RS92 set sonde = 2

if sonde == 2
    t = fullfile(d, "*.csv");
    files = dir(t);
else
    t = fullfile(d, "*.txt");
    files = dir(t);
end
for i=1:size(files)
    current = files(i).name;
    current = fullfile(d, current);
    if sonde == 2
        data = readRS92Data(current);
    else
        data = readRadioSondeData(current);
    end
    
    [~, idx] = max(data.Alt);
    data = data(1:idx, :);
    data = data(data.Alt > 12000, :);
    if isempty(data)
        continue;
    end
    if sonde == 2
        RS = 5;
    else
        RS = mean(data.Rs);
    end
    
    u = -(data.Ws) .* sind(data.Wd); % from MetPy
    v = -(data.Ws) .* cosd(data.Wd); %    
    subplot(2, 1, 1)
    [Alt, u, v, temp, bvFreqSquared] = ... 
        preprocessDataNoResample(data.Alt, u, v, data.T, data.P, RS);
    while(true)
        subplot(1, 3, 1);
        plot(u, Alt, 'b');
        title uVSaltitude;
        subplot(1, 3, 2);
        plot(v, Alt, 'r');
        title vVSaltitude;
        sgtitle(files(i).name, 'Interpreter', 'none');
        [x, y] = ginput(2);
        [~, Alt_1] = min(abs(Alt - y(1)));
        [~, Alt_2] = min(abs(Alt - y(2)));
        %[~, Alt_1] = min(abs(Alt - 22.55*1000));
        %[~, Alt_2] = min(abs(Alt - 22.1*1000));
        upper = max(Alt_1, Alt_2);
        lower = min(Alt_1, Alt_2);
        subplot(1, 3, 3);
        plot(u(lower:upper), v(lower:upper));
        title HodographEllipse;
        subplot(1, 3, 1);
        hold on;
        
        plot(u(lower), Alt(lower), 'ro','MarkerSize', 14);
        plot(u(upper), Alt(upper), 'bo', 'MarkerSize', 14);
        fprintf("%d, %d\n", Alt(lower), Alt(upper));
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
            T = table(Alt(lower:upper), u(lower:upper), v(lower:upper), temp(lower:upper), bvFreqSquared(lower:upper));
            T.Properties.VariableNames = {'Alt' 'u' 'v' 'temp' 'bv2'};
            [~, n, ~] = fileparts(files(i).name);
            fname = sprintf(".\\hodograph\\%s-%d-%d.txt", n, Alt(lower), Alt(upper));
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