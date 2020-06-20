classdef WindowedWaveletTransform
    % Container class to store indices
    % of the windowed wavelet transform.
    properties
        scale_index_1;
        scale_index_2;
        alt_index_1;
        alt_index_2;
    end
    
    methods
        function obj = WindowedWaveletTransform(scale_index_1, scale_index_2, alt_index_1, alt_index_2)
            %UNTITLED Construct an instance of this class
            %   Detailed explanation goes here
            obj.scale_index_1 = scale_index_1;
            obj.scale_index_2 = scale_index_2;
            obj.alt_index_1 = alt_index_1;
            obj.alt_index_2 = alt_index_2;

        end
    end
end

