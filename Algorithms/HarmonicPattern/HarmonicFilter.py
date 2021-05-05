import numpy as np

# ---------- filter patterns function
def filter_results(high, low, res, middle, harmonic_name, trend_direction):
    if len(res) == 0:
        return

    # define Candle Size
    res = get_pattern_size(res) # 1 to 5 from very small to very larg.very small, small, medium, large, very large
    filter_mode = 'Percent'
    res = eliminate_duplicate_patterns(res, trend_direction)

    if filter_mode == 'std':
        res = eliminate_high_std_patterns(res, middle)
    elif filter_mode == 'Percent':
        alpha = .37 # .37 STD coefficient.higher led to bigger channel
        beta = .94 # .94 percent of should be in the channel
        res = eliminate_out_of_bound_patterns(res, middle, Low, High, harmonic_name, alpha, beta)

    # ---- check the ratio is near to fibonacci number or not
    res = check_the_fibbo_ratio(res, harmonic_name, trend_direction)

    # # ------- filter based on the Vortex
    res = is_vertex_of_harmonic_extremum(d, res, trend_direction) # add short term trend and long treme trend to the results
    res = check_vertex(harmonic_name, res)
    return res

# -- filte based on STD
def eliminate_high_std_patterns(res, middle):
    x_idx = 0
    a_idx = 1
    b_idx = 2
    c_idx = 3
    d_idx = 4

    situation = [False] * len(res)
    for i in range(len(res)):
        situation_x_a = check_std_of_waves(res[i][x_idx:a_idx], middle[res[i][x_idx]: res[i][a_idx]])
        situation_a_b = check_std_of_waves(res[i][a_idx:b_idx], middle[res[i][a_idx]: res[i][b_idx]])
        situation_b_c = check_std_of_waves(res[i][b_idx:c_idx], middle[res[i][b_idx]: res[i][c_idx]])
        situation_c_d = check_std_of_waves(res[i][c_idx:d_idx], middle[res[i][c_idx]: res[i][d_idx]])
        if situation_x_a and situation_a_b and situation_b_c and situation_c_d:
            situation[i] = True
        res[i].append(situation[i])

function
situation = checkSTDOfWaves(rng, c)
alpha = 2; % STD
coefficient
beta = .85; % numberr
of
candles
which
be
out
of
theSTD
boundery
situation = false;
Rng = (rng(1):rng(end))';
p = polyfit([rng(1);
rng(end)], [c(1);
c(end)], 1);
line = polyval(p, Rng);

lowerSTD = line - alpha. * std(line);
upperSTD = line + alpha. * std(line);

if sum(c >= lowerSTD) > numel(lowerSTD) * beta & & sum(c <= upperSTD) > numel(lowerSTD) * beta
    situation = true;
end
end

% classifiy
pattern
by
their
size
function
res = GetPatternSize(res)
xIdx = 1;
aIdx = 2;
bIdx = 3;
cIdx = 4;
dIdx = 5;

tr1 = 15;
tr2 = 30;
tr3 = 45;
tr4 = 60;

pattSize = zeros(size(res, 2), 1);
for i=1:size(res, 2)
PatternLen = res(dIdx, i) - res(xIdx, i);
if PatternLen <= tr1
    pattSize(i) = 1;
elseif
PatternLen > tr1 & & PatternLen <= tr2
pattSize(i) = 2;
elseif
PatternLen > tr2 & & PatternLen <= tr3
pattSize(i) = 3;
elseif
PatternLen > tr3 & & PatternLen <= tr4
pattSize(i) = 4;
elseif
PatternLen > tr4
pattSize(i) = 5;
end
end
res = [res;
pattSize
'];
end

% -- filter
Based
on
percentage
of
line
function
res = EliminateOutOfBoundPatterns(res, c, Low, High, HarmonicName, alpha, beta)
meanOfCandle = mean(High - Low);

c = mean([High Low], 2);
% High = High - mean(c);
% Low = Low - mean(c);
% c = c - mean(c);
High = (c);
Low = c;

xIdx = 1;
aIdx = 2;
bIdx = 3;
cIdx = 4;
dIdx = 5;

situation = false(size(res, 2), 1);

for i = 1:size(res, 2)
rng = res(xIdx, i):res(aIdx, i);

p = polyfit([rng(1);
rng(end)], [Low(rng(1));
High(rng(end))], 1);
l = polyval(p, rng);
[lowerBound, upperBound] = FindBoundery(meanOfCandle, c, Low(rng(1)), High(rng(end)), rng, l, alpha); % XA
Leg
situationXA = sum(lowerBound < Low(rng) & High(rng) < upperBound) >= numel(rng) * beta;
if strcmpi(HarmonicName, 'ABCD')
situationXA = true;
end

rng = res(aIdx, i):res(bIdx, i);

p = polyfit([rng(1);
rng(end)], [High(rng(1));
Low(rng(end))], 1);
l = polyval(p, rng);
[lowerBound, upperBound] = FindBoundery(meanOfCandle, c, High(rng(1)), Low(rng(end)), rng, l, alpha); % AB
Leg
situationAB = sum(lowerBound < Low(rng) & High(rng) < upperBound) >= numel(rng) * beta;

rng = res(bIdx, i):res(cIdx, i);

p = polyfit([rng(1);
rng(end)], [Low(rng(1));
High(rng(end))], 1);
l = polyval(p, rng);
[lowerBound, upperBound] = FindBoundery(meanOfCandle, c, Low(rng(1)), High(rng(end)), rng, l, alpha); % BC
Leg
situationBC = sum(lowerBound < Low(rng) & High(rng) < upperBound) >= numel(rng) * beta;

rng = res(cIdx, i):res(dIdx, i);

p = polyfit([rng(1);
rng(end)], [High(rng(1));
Low(rng(end))], 1);
l = polyval(p, rng);
[lowerBound, upperBound] = FindBoundery(meanOfCandle, c, High(rng(1)), Low(rng(end)), rng, l, alpha); % CD
Leg
situationCD = sum(lowerBound < Low(rng) & High(rng) < upperBound) >= numel(rng) * beta;

if situationXA & & situationAB & & situationBC & & situationCD
situation(i) = true;
end
end
res = res(:, situation);
end
function[alpha, beta] = GetTheCoefficientOFBound(rng1, rng2)
tr1 = 8;
tr2 = 20;
tr3 = 40;
tr4 = 70;

if rng2 - rng1 <= tr1
alpha = .60;
beta = .92;
elseif
rng2 - rng1 >= tr1 & & rng2 - rng1 < tr2
alpha = .63;
beta = .92;
elseif
rng2 - rng1 >= tr2 & & rng2 - rng1 < tr3
alpha = .64;
beta = .92;
elseif
rng2 - rng1 >= tr3 & & rng2 - rng1 < tr4
alpha = .65;
beta = .92;
elseif
rng2 - rng1 >= tr4
alpha = .70;
beta = .92;
end

end
function[lowerBoundHat, upperBoundHat] = FindBoundery(meanOfCandle, c, startVal, endVal, x, y, alpha) \
                                         % alpha = .50;
% % Example
coordinates
% y = [1 4 7 10 13 16];
% x = 101:numel(y) + 100;

% ------------------ find
the
rotation
degree
slope = rad2deg(atan((endVal - startVal) / (x(end) - x(1))));

% ------------------ rotate
line
[xHat, yHat] = RotateLine(x, y, -slope);

% ------------------ find
bound
of
line \
% upperBound = yHat * (1 + alpha);
% lowerBound = yHat * (1 - alpha);
upperBound = yHat + (1 + alpha) * std(c(x));
lowerBound = yHat - (1 + alpha) * std(c(x));
% ------------------ de - rotate
boundery
lines
[~, upperBoundHat] = RotateLine(xHat, upperBound, slope);
[~, lowerBoundHat] = RotateLine(xHat, lowerBound, slope);

isPlot = false;
if isPlot
figure;
plot([x(1);
x(end)], [startVal;
endVal], 'b:', 'MarkerSize', 25);  hold
on; % Original
plot(x, c(x), 'k.-', 'MarkerSize', 25);
hold
on; % middle
Of
Candle
plot(x, upperBoundHat, 'r.-', 'MarkerSize', 8); % Rotated
around
centre
of
line
plot(x, lowerBoundHat, 'r.-', 'MarkerSize', 8); % Rotated
around
centre
of
line
grid
on;
end
end
function[x, y] = RotateLine(x, y, Deg)
                 % Vertices
matrix
V = [x(:) y(:) zeros(size(y(:)))];
V_centre = mean(V, 1); % Centre, of
line
Vc = V - ones(size(V, 1), 1) * V_centre; % Centering
coordinates
a_rad = ((Deg * pi). / 180); % Angle in radians
E = [0  0 a_rad]; % Euler
angles
for X, Y, Z - axis rotations

                   % Direction Cosines (rotation matrix) construction
Rx=[1        0        0;...
0        cos(E(1))  -sin(E(1));...
0        sin(E(1))  cos(E(1))]; % X-Axis rotation
Ry=[cos(E(2))  0        sin(E(2));...
0        1        0;...
-sin(E(2)) 0        cos(E(2))]; % Y-axis rotation
Rz=[cos(E(3))  -sin(E(3)) 0;...
sin(E(3))  cos(E(3))  0;...
0        0        1]; % Z-axis rotation
R   = Rx * Ry * Rz; % Rotation matrix
Vrc = (R * Vc')'; % Rotating centred coordinates
Vr  = Vrc+ones(size(V, 1), 1) * V_centre; % Shifting back to original location
x   = Vr(:,
    1);
y = Vr(:, 2);

end
% eliminate
duplicate
pattern
with common D point
function uniquePatterns = EliminateDuplicatePatterns(res, TrendDirection)
dIdx    = 5;
xValIdx = 6;
aValIdx = 7;
bValIdx = 8;
cValIdx = 9;

if strcmpi(TrendDirection, 'Bearish')
str = {'ascend' 'descend' 'ascend' 'descend'};
elseif strcmpi(TrendDirection, 'Bullish')
str = {'descend' 'ascend' 'descend' 'ascend'};
end
if isempty(res)
return;
end
uniqueMem = unique(res(dIdx,:));
uniquePatterns = zeros(size(res, 1), numel(uniqueMem));
for i=1:length(uniqueMem)
uniqueIdx = uniqueMem(i) == res(dIdx,:);
% -------- select
best
patterns, Bullish
Patterns
[B, ~] = sortrows(res(:, uniqueIdx)',[cValIdx xValIdx aValIdx bValIdx  ],str);
uniquePatterns(:, i) = B(1,:)';
end
end

function
res = Checkvertex(HarmonicName, res)
if strcmpi(HarmonicName, 'ABCD')
alpha = 2;
res = res(:, sum(res(end - 2: end,:)) >= alpha & res(end - 1,:) == 1 & res(end,:) == 1);
else
alpha = 3;
res = res(:, sum(res(end - 3: end,:)) >= alpha & res(end - 1,:) == 1 & res(end,:) == 1);
end
end

% ---
function
res = CheckTheFibboRatio(res, HarmonicName, TrendDirection)

end
