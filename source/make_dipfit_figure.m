clear; close all; clc;
root = fileparts(mfilename('fullpath'));
outdir = fullfile(root, 'eeglab_octave_outputs');
figdir = fullfile(root, 'analysis_outputs');
addpath(fullfile(root, 'octave_compat'), '-begin');
addpath(fullfile(root, 'eeglab', 'functions', 'adminfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'guifunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'popfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'sigprocfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'miscfunc'));
addpath(fullfile(root, 'eeglab', 'plugins', 'dipfit2.3'));
graphics_toolkit('gnuplot');
set(0, 'defaultfigurevisible', 'off');
EEG = pop_loadset('filename', 'yyw2_target_ICA_DIPFIT.set', 'filepath', outdir);
fprintf('Loaded DIPFIT dataset: component 1 RV=%g\n', EEG.dipfit.model(1).rv);
% Visualize the actual EEGLAB DIPFIT result on its BESA spherical head model.
% This avoids MRI-slice rendering differences in Octave while preserving the
% measured position, moment and residual variance from the saved dataset.
mdl = EEG.dipfit.model(1);
p = mdl.posxyz(1,:); m = mdl.momxyz(1,:);
if norm(m) > 0, u = 25*m/norm(m); else, u = [0 0 20]; end
[sx, sy, sz] = sphere(48);
surf(85*sx, 85*sy, 85*sz, 'FaceAlpha', 0.12, 'EdgeColor', [0.55 0.55 0.55]);
hold on; axis equal; grid on;
scatter3(p(1), p(2), p(3), 100, 'r', 'filled');
quiver3(p(1), p(2), p(3), u(1), u(2), u(3), 0, 'r', 'LineWidth', 2, 'MaxHeadSize', 0.7);
text(p(1), p(2), p(3), '  IC1', 'Color', 'r', 'FontWeight', 'bold');
xlabel('X (mm)'); ylabel('Y (mm)'); zlabel('Z (mm)');
title(sprintf('EEGLAB DIPFIT: IC1, grid-fit RV = %.3f%%', 100*mdl.rv));
view(135, 25); xlim([-90 90]); ylim([-90 90]); zlim([-90 90]);
annotation('textbox', [0.02 0.02 0.96 0.08], 'String', sprintf('Position = [%.1f, %.1f, %.1f] mm   |   Moment = [%.1f, %.1f, %.1f]   |   20-channel grid fit', p(1),p(2),p(3),m(1),m(2),m(3)), 'FitBoxToText', 'off', 'EdgeColor', 'none', 'HorizontalAlignment', 'center');
drawnow;
print(gcf, fullfile(figdir, '10_DIPFIT_good_component.png'), '-dpng', '-r150');
savefig(gcf, fullfile(figdir, '10_DIPFIT_good_component.fig'));
fprintf('Saved %s\n', fullfile(figdir, '10_DIPFIT_good_component.png'));
exit;
