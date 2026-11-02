% Continue the real EEGLAB workflow from the already saved target epochs.
clear; close all; clc;
root = fileparts(mfilename('fullpath'));
outdir = fullfile(root, 'eeglab_octave_outputs');
addpath(fullfile(root, 'octave_compat'), '-begin');
addpath(fullfile(root, 'eeglab', 'functions', 'adminfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'guifunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'popfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'sigprocfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'miscfunc'));
addpath(fullfile(root, 'eeglab', 'plugins', 'firfilt1.6.1'));

fprintf('Load EEGLAB target epochs for ICA\n');
ICAEEG = pop_loadset('filename', 'yyw2_target_epochs_clean.set', 'filepath', outdir);
fprintf('Loaded target epochs: %d channels, %d points, %d trials\n', ICAEEG.nbchan, ICAEEG.pnts, ICAEEG.trials);
fprintf('Prepare ICA data with 1-30 Hz FIR filter\n');
ICAEEG = pop_eegfiltnew(ICAEEG, 1, 30, [], 0, [], 0);
fprintf('Run EEGLAB runica\n');
ICAEEG = pop_runica(ICAEEG, 'icatype', 'runica', 'extended', 1, 'interupt', 'off');
ICAEEG.setname = 'yyw2_target_ICA';
ICAEEG = eeg_checkset(ICAEEG);
fprintf('ICA components: %d\n', size(ICAEEG.icaweights, 1));
pop_saveset(ICAEEG, 'filename', 'yyw2_target_ICA.set', 'filepath', outdir, 'savemode', 'twofiles');
save(fullfile(outdir, 'eeglab_ica_workspace.mat'), 'ICAEEG', '-v7');
fid = fopen(fullfile(outdir, 'eeglab_ica_history.txt'), 'w');
fprintf(fid, '%s\n', ICAEEG.history);
fclose(fid);
fprintf('EEGLAB ICA complete.\n');
exit;
