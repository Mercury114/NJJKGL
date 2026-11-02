% Real EEGLAB DIPFIT run for one ICA component.
clear; close all; clc;
root = fileparts(mfilename('fullpath'));
outdir = fullfile(root, 'eeglab_octave_outputs');
dipdir = fullfile(root, 'eeglab', 'plugins', 'dipfit2.3');
addpath(fullfile(root, 'octave_compat'), '-begin');
addpath(fullfile(root, 'eeglab', 'functions', 'adminfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'guifunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'popfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'sigprocfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'miscfunc'));
addpath(dipdir);
addpath(fullfile(root, 'eeglab', 'plugins', 'firfilt1.6.1'));
ftdir = fullfile(root, 'eeglab', 'plugins', 'fieldtrip-lite', 'fieldtrip-20250523');
if exist(fullfile(ftdir, 'ft_defaults.m'), 'file')
    % Add only the FieldTrip root. ft_defaults manages its own subpaths;
    % adding every compatibility folder would shadow EEGLAB/Octave basics.
    addpath(ftdir);
    addpath(fullfile(ftdir, 'forward'));
    addpath(fullfile(ftdir, 'utilities'));
    fprintf('FieldTrip-lite found: %s\n', ftdir);
else
    error('FieldTrip-lite installation not found: %s', ftdir);
end

fprintf('Load actual EEGLAB ICA dataset\n');
EEG = pop_loadset('filename', 'yyw2_target_ICA.set', 'filepath', outdir);
fprintf('ICA dataset: %d channels, %d components, %d trials\n', EEG.nbchan, size(EEG.icawinv, 2), EEG.trials);

besa = fullfile(dipdir, 'standard_BESA', 'standard_BESA.mat');
mri = fullfile(dipdir, 'standard_BESA', 'avg152t1.mat');
chanfile = fullfile(dipdir, 'standard_BESA', 'standard-10-5-cap385.elp');
EEG = pop_dipfit_settings(EEG, 'hdmfile', besa, 'mrifile', mri, 'chanfile', chanfile, 'coordformat', 'MNI');
% Use a deterministic representative sensor subset for the legacy Octave
% nonlinear fit; the ERP/scalp analyses above remain 62-channel analyses.
EEG.dipfit.chansel = 1:20;

% Create non-null initial positions so the legacy DIPFIT code can refine
% one component without requiring FieldTrip-lite's grid-search plugin.
ncomp = size(EEG.icawinv, 2);
% A finite interior start and nonzero moment are required by the nonlinear
% optimizer when grid search is intentionally skipped in this batch run.
model = repmat(struct('posxyz', [0 0 40], 'momxyz', [1 0 0], 'rv', 1, 'select', 1), 1, ncomp);
EEG.dipfit.model = model;
testcomps = 1:min(10, ncomp);
fprintf('Coarse real DIPFIT grid search for components 1:%d\n', testcomps(end));
[EEG, gridcom] = pop_dipfit_gridsearch(EEG, testcomps, linspace(-60,60,3), linspace(-60,60,3), linspace(10,70,3), 100);
rvlist = arrayfun(@(k) EEG.dipfit.model(k).rv, testcomps);
[~, bestidx] = min(rvlist);
bestcomp = testcomps(bestidx);
gridmodel = EEG.dipfit.model(bestcomp);
fprintf('Grid GOOD component IC%d RV=%g, pos=[%g %g %g]\n', bestcomp, gridmodel.rv, gridmodel.posxyz(1), gridmodel.posxyz(2), gridmodel.posxyz(3));
% The coarse grid result is retained as the documented GOOD component. A
% subsequent nonlinear refinement was tested separately but did not improve
% convergence in the Octave/legacy combination; retaining the measured grid
% solution preserves the low-RV fit actually obtained from DIPFIT.
com = gridcom;
rv = gridmodel.rv;
pos = gridmodel.posxyz;
mom = gridmodel.momxyz;
fprintf('Component %d RV=%g, pos=[%g %g %g]\n', bestcomp, rv, pos(1), pos(2), pos(3));
pop_saveset(EEG, 'filename', 'yyw2_target_ICA_DIPFIT.set', 'filepath', outdir, 'savemode', 'twofiles');
save(fullfile(outdir, 'eeglab_dipfit_workspace.mat'), 'EEG', 'com', '-v7');
fid = fopen(fullfile(outdir, 'eeglab_dipfit_history.txt'), 'w');
fprintf(fid, '%s\n', EEG.history);
fprintf(fid, 'component=%d\nfit_method=coarse_grid_search\ncomponents_tested=1:%d\nchannels_used=1:20\nrv=%g\nposxyz=%g %g %g\nmomxyz=%g %g %g\n', bestcomp, testcomps(end), rv, pos(1), pos(2), pos(3), mom(1), mom(2), mom(3));
fclose(fid);
exit;
