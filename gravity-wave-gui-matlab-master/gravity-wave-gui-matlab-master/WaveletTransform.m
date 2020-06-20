classdef WaveletTransform
    %WaveletTransform 
    %   This class acts as a logical grouping of variables for a wavelet
    %   transform. The transform and inverse transform rely on the
    %   same parameters (s0, dj, dt) so keeping the parameters grouped with
    %   the transform will reduce the mental overhead incurred by trying to
    %   pass the same set of parameters to the forward and backward
    %   transform.
    
    properties
        s0;
        dj;
        dt;
        u_wind_component;
        v_wind_component;
        powerSurface;
        uWavelet;
        vWavelet;
        waveletScales;
        fourierWavelength;
        tempWavelet;
        coi;
        alt;
        sig95;
    end
    
    methods
        function obj = WaveletTransform(u_wind_component, v_wind_component, temperature, dt)
            %UNTITLED3 Construct an instance of this class
            %   Detailed explanation goes here
            pad = 1; % Use padding to help with edge effects.
            dj = 0.125/8; % Value of dj determines scale resolution of the transform.
            s0 = 2*dt; % Minimum resolvable scale. dt is just the sampling rate -
            % either in time or space.
            obj.u_wind_component = u_wind_component;
            obj.v_wind_component = v_wind_component;
            obj.s0 = s0;
            obj.dj = dj;
            obj.dt = dt;
            [obj.uWavelet, ~, obj.waveletScales, ~] = wavelet(u_wind_component, dt, pad, dj, s0); % wave, period, scale, COI
            lag1 = acf(u_wind_component', 1);
            [sigU, ~] = wave_signif(u_wind_component, dt, obj.waveletScales, 0, lag1);
            [obj.vWavelet, ~, ~, obj.coi] = wavelet(v_wind_component, dt, pad, dj, s0); % coi is the same for all transforms of the same data.
            lag1 = acf(v_wind_component', 1);
            [obj.tempWavelet, ~, ~, ~] = wavelet(temperature, dt, pad, dj, s0);
            [sigV, ~] = wave_signif(v_wind_component, dt, obj.waveletScales, 0, lag1);
            obj.sig95 = (sigU + sigV)'*(ones(1,size(u_wind_component, 2)));
            obj.powerSurface = abs(obj.uWavelet).^2 + abs(obj.vWavelet).^2;
            obj.sig95 = obj.powerSurface ./ obj.sig95;
            obj.fourierWavelength = 1.03 * obj.waveletScales; % magic number from Torrence and Compo.
        end
        
        function [u_wind_reconstructed, v_wind_reconstructed, tempReconstructed, meanVerticalWavelength, windVariance] = invertWindowedTransform(obj, windowedWaveletTransform)
            % Reconstruct the wave packet at altitudes of interest and
            % scales of interest by adding up the wavelet coefficients at
            % the scales of interest. This is an implementation of equation
            % 11 in Torrence and Compo, 1998. The difference is that we
            % keep both the real and imaginary parts of the reconstruction
            % to use in later analysis.
            scale_index_1 = windowedWaveletTransform.scale_index_1;
            scale_index_2 = windowedWaveletTransform.scale_index_2;
            alt_index_1 = windowedWaveletTransform.alt_index_1;
            alt_index_2 = windowedWaveletTransform.alt_index_2;
            constant_coef = obj.dj * sqrt(obj.dt) / (0.776*pi^(1/4)); % Constant from Torrence and Compo, 1998, given in
            % table 2 and applied in equation 11.
            windowed_scales = obj.waveletScales(scale_index_1:scale_index_2);
            windowed_u_wavelet = obj.uWavelet(scale_index_1:scale_index_2, alt_index_1:alt_index_2);
            u_wind_reconstructed = constant_coef*sum(windowed_u_wavelet ./ sqrt(windowed_scales)', 1); % sum over all scales.
            windowed_v_wavelet = obj.vWavelet(scale_index_1:scale_index_2, alt_index_1:alt_index_2);
            windowedTempWavelet = obj.tempWavelet(scale_index_1:scale_index_2, alt_index_1:alt_index_2);
            tempReconstructed = constant_coef*sum(windowedTempWavelet ./ sqrt(windowed_scales)', 1);
            v_wind_reconstructed = constant_coef*sum(windowed_v_wavelet ./ sqrt(windowed_scales)', 1);
            meanVerticalWavelength = mean(obj.fourierWavelength(scale_index_1:scale_index_2)); % the dominant wavelength is taken
            % to be the mean of the wavelengths over the scale range of
            % interest. Same as in Murphy, 2014.
            windVariance = abs(u_wind_reconstructed).^2 + abs(v_wind_reconstructed).^2;
        end
        
        function [uWindInverted, vWindInverted] = invertWaveletTransform(obj)
            % This inverts the entire wavelet transform.
           constantCoef = obj.dj * sqrt(obj.dt) / (0.776*pi^(1/4)); % Magic from T&C.
           uWindInverted = constantCoef*sum(real(obj.uWavelet) ./ sqrt(obj.waveletScales)', 1); % sum over scales
           vWindInverted = constantCoef*sum(real(obj.vWavelet) ./ sqrt(obj.waveletScales)', 1); 
           
        end
        
        function [a, b, c, d] = clipWindowedTransformToValue(obj, localMaxRow, localMaxCol)
            % clipWindowedTransformToValue either clips the windowed
            % transform to thresholdValue, or clips it to the next point
            % where the surface starts rising again.
            maxValue = obj.powerSurface(localMaxRow, localMaxCol);    
            thresholdValue = 0.25*maxValue;
            column = obj.powerSurface(:, localMaxCol); % extract whole column
            row = obj.powerSurface(localMaxRow, :); % extract whole row
            % need the locations of the first minima on each side of the
            % local max in both row and column. These locations will define
            % the windowed power surface before we clip it to
            % thresholdValue.
            [a, b] = findMinimaClosestToIndex(abs(column-thresholdValue), localMaxRow);
            [c, d] = findMinimaClosestToIndex(abs(row-thresholdValue), localMaxCol);
            % index into this window and make sure there's only
            % one peak inside this window.
            if b > size(obj.powerSurface, 1)
                x = size(obj.powerSurface, 1);
                fprintf("%d , %d\n", x, b);
            end
            if d > size(obj.powerSurface, 2)
                x = size(obj.powerSurface, 2);
                fprintf("%d , %d\n", x, d);
            end
            
        end

    end
end

