data_dir = '/Users/thomascolligan/box/Eclipse 2019/Practice_Flight_Data/Profile';
t = fullfile(data_dir, "*.txt");
files = dir(t);

for i=1:size(files)
    current = files(i).name;
    try
        if ~contains(current, 'W4_L2')
            continue;
        end

        current = fullfile(data_dir, current);
        data = readRadioSondeData(current); 
        
        plot(data.Alt)
        % rs = data.Rs(1:mai);
        % fprintf("Current file: %s. Max alt: %f, Avg rise rate: %f\n", current, maxAlt, mean(rs));
    catch e
        if (strcmp(e.identifier, 'MATLAB:table:UnrecognizedVarName'))
            fprintf("----------------------------\n");
            fprintf("Exception occured when reading file %s with message:\n%s\n", current, e.message);
            fprintf("----------------------------\n");
            continue;
        end
        rethrow(e);
    end
        fprintf("----------------------------\n");

end

