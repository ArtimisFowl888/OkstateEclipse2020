data_dir = '/Users/thomascolligan/Box/Eclipse 2019/Practice_Flight_Data/Profile';
t = fullfile(data_dir, "*.txt");
files = dir(t);
maxLength = 0;
k = 0;
launchSite = 'Lusk';
for i=1:size(files)
    current = files(i).name;
    current = fullfile(data_dir, current);
    data = readRadioSondeData(current);
    try
        if max(data.Alt) < 10000
            continue
        end
        if size(data, 1) > maxLength
            maxLength = size(data, 1);
        end
        k = k + 1;
    catch
        continue
    end
end

dataBlock = zeros(600, k);
counter = 1;
for i=1:size(files)
   current = files(i).name;
   current = fullfile(data_dir, current);
   data = readRadioSondeData(current);
   try
   alt = data.Alt;
   [~, mai] = max(alt);
   alt = data.Alt(1:mai);
   ws = data.Ws(1:mai);
   wd = data.Wd(1:mai);
   catch
       %fprintf("Reading data from %s failed.\n", current);
       continue
   end
   fprintf("F: %s\n", current);
   u = ws.*cosd(wd);
   v = ws.*sind(wd);
   time = data.Time(1:mai);
   u = fitAndRemovePolynomial(time, u, 3);
   v = fitAndRemovePolynomial(time, v, 3);
   u = averageToAltitudeResolution(u, alt, 50);
   v = averageToAltitudeResolution(v, alt, 50);
   j = size(u, 2);
   dataBlock(1:j, counter) = u.^2 + v.^2;
   counter = counter + 1;
end
contourf(log2(dataBlock))


