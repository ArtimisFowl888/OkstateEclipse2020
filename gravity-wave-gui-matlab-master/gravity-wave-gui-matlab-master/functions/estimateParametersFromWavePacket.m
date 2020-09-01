  function [D, P, Q, theta, axialRatio, degreeOfPolarization] = estimateParametersFromWavePacket(uWavePacket, vWavePacket, tempWavePacket)
%   Estimate gravity wave parameters from a wave packet using the Stokes
%   parameters method.
u = real(uWavePacket);
v = real(vWavePacket);
vWavePacketHilbertTransformed = imag(vWavePacket);
% Stokes parameters from Murphy et al, 2014, Appendix A.
I = mean(u.^2) + mean(v.^2);
D = mean(u.^2) - mean(v.^2);
P = mean(2*u.*v);
Q = mean(2*u.*vWavePacketHilbertTransformed);
degreeOfPolarization = sqrt((P^2 + Q^2 + D^2)) / I;
% perform filtering based on Stokes parameters and degree of polarization.
% TODO test DOP threshold values and examine 'depolarization' in Murphy et
% al
if abs(Q) < 0.05 || abs(P) < 0.05 || degreeOfPolarization < 0.5 || degreeOfPolarization > 1
    theta = 0;
    axialRatio = 0;
    degreeOfPolarization = 0;
    Q = 0;
    return;
else
    theta = 0.5 * atan2(P, D); % Zink, 2000 eqn 3.14 TODO investigate atan2
    % Axial ratio
    axialRatio = abs(cot(0.5*asin(Q/(degreeOfPolarization*I))));
    % Murphy et al (2014), Koushik et al (2019), and Vincent (1989)
    % Look at phase b/t u' and T+90'
    % From the polarization relations, we know that u' and T' are +-90 deg
    % out of phase, depending on the sign of the horizontal wavenumber. The 
    % polarization relations are in a frame that is traveling with the wave 
    % in the same direction, so we have to rotate the zonal wind component 
    % (u) to align with the wave's direction.
    rotationMatrix = [cos(theta) sin(theta); -sin(theta) cos(theta)];
    uv = [uWavePacket; vWavePacket];
    uvRotated = rotationMatrix * uv;
    % axialRatio = abs(mean(uv(1, :)) / mean(uv(2, :)));
    uPar = uvRotated(1, :);
    % vPerp = uvRotated(2, :);
    gamma = mean(uPar.*conj(tempWavePacket)) ./ sqrt(mean(abs(uPar).^2).*mean(abs(tempWavePacket).^2));
    phase = atan2(imag(gamma), real(gamma));
    if phase <= 0
        theta = theta + pi;
    end
    if axialRatio < 1
        % i.e. if the intrinsic frequency is less than the coriolis
        % frequency. This does not agree with theory, so the wave packet 
        % is discarded.
        % Assing NaN to unphysical values?
        theta = 0;
        axialRatio = 0;
        degreeOfPolarization = 0;
        Q = 0;
        return;
    end
end
end

