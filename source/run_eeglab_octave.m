% Real EEGLAB/Octave reproduction of the experiment guide workflow.
% This script uses EEGLAB's pop_loadcnt/loadcnt and pop_* functions.
clear; close all; clc;
root = fileparts(mfilename('fullpath'));
outdir = fullfile(root, 'eeglab_octave_outputs');
if ~exist(outdir, 'dir'), mkdir(outdir); end
addpath(fullfile(root, 'octave_compat'), '-begin');
addpath(fullfile(root, 'eeglab', 'functions', 'adminfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'guifunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'popfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'sigprocfunc'));
addpath(fullfile(root, 'eeglab', 'functions', 'miscfunc'));
addpath(fullfile(root, 'eeglab', 'plugins', 'firfilt1.6.1'));

fprintf('EEGLAB CNT import start\n');
EEG = pop_loadcnt(fullfile(root, 'yyw2_train.cnt'), 'dataformat', 'auto', 'memmapfile', '');
EEG.setname = 'yyw2_raw';
EEG = eeg_checkset(EEG);
fprintf('Imported: %d channels, %g Hz, %d points, %d events\n', EEG.nbchan, EEG.srate, EEG.pnts, length(EEG.event));
pop_saveset(EEG, 'filename', 'yyw2_raw.set', 'filepath', outdir, 'savemode', 'twofiles');

fprintf('Load channel locations and remove M1/M2\n');
origlabels = { EEG.chanlocs.labels };
try
    EEG = pop_chanedit(EEG, 'load', { fullfile(root, '64-channels.loc') 'filetype' 'loc' });
    for k = 1:min(length(origlabels), length(EEG.chanlocs))
        EEG.chanlocs(k).labels = origlabels{k};
    end
catch err
    fprintf('Channel-location GUI function unavailable; retaining CNT channel labels: %s\n', err.message);
end
EEG = pop_select(EEG, 'nochannel', {'M1' 'M2'});
EEG = eeg_checkset(EEG);

fprintf('Resample 1000 -> 250 Hz\n');
EEG = pop_resample(EEG, 250);
fprintf('Average reference\n');
EEG = pop_reref(EEG, []);
fprintf('FIR band-pass 0.1-15 Hz\n');
EEG = pop_eegfiltnew(EEG, 0.1, 15, [], 0, [], 0);
EEG.setname = 'yyw2_preprocessed_250Hz';
EEG = eeg_checkset(EEG);
pop_saveset(EEG, 'filename', 'yyw2_preprocessed_250Hz.set', 'filepath', outdir, 'savemode', 'twofiles');

fprintf('Extract target epochs, baseline -200..0 ms\n');
TARGET = pop_epoch(EEG, { 1 }, [-0.2 1.0], 'newname', 'yyw2_target_epochs', 'epochinfo', 'yes');
TARGET = pop_rmbase(TARGET, [-200 0], []);
TARGET = eeg_checkset(TARGET);
TARGET = pop_eegthresh(TARGET, 1, 1:TARGET.nbchan, -150, 150, -0.2, 1.0, 0, 0);
target_rej = find(TARGET.reject.rejthresh);
if ~isempty(target_rej), TARGET = pop_rejepoch(TARGET, target_rej, 0); end
TARGET.setname = 'yyw2_target_epochs_clean';
TARGET = eeg_checkset(TARGET);
pop_saveset(TARGET, 'filename', 'yyw2_target_epochs_clean.set', 'filepath', outdir, 'savemode', 'twofiles');
fprintf('Target epochs after threshold rejection: %d\n', TARGET.trials);

fprintf('Extract non-target epochs, baseline -200..0 ms\n');
NONTARGET = pop_epoch(EEG, { 2 }, [-0.2 1.0], 'newname', 'yyw2_nontarget_epochs', 'epochinfo', 'yes');
NONTARGET = pop_rmbase(NONTARGET, [-200 0], []);
NONTARGET = eeg_checkset(NONTARGET);
NONTARGET = pop_eegthresh(NONTARGET, 1, 1:NONTARGET.nbchan, -150, 150, -0.2, 1.0, 0, 0);
nontarget_rej = find(NONTARGET.reject.rejthresh);
if ~isempty(nontarget_rej), NONTARGET = pop_rejepoch(NONTARGET, nontarget_rej, 0); end
NONTARGET.setname = 'yyw2_nontarget_epochs_clean';
NONTARGET = eeg_checkset(NONTARGET);
pop_saveset(NONTARGET, 'filename', 'yyw2_nontarget_epochs_clean.set', 'filepath', outdir, 'savemode', 'twofiles');
fprintf('Non-target epochs after threshold rejection: %d\n', NONTARGET.trials);

fprintf('Core preprocessing and epoch workflow complete; ICA is run by run_eeglab_ica.m\n');
save(fullfile(outdir, 'eeglab_workspace.mat'), 'EEG', 'TARGET', 'NONTARGET', '-v7');
fid = fopen(fullfile(outdir, 'eeglab_history.txt'), 'w');
fprintf(fid, 'EEGLAB/Octave run on %s\n\n', datestr(now));
fprintf(fid, 'RAW history:\n%s\n', EEG.history);
fprintf(fid, 'TARGET history:\n%s\n', TARGET.history);
fprintf(fid, 'NONTARGET history:\n%s\n', NONTARGET.history);
fclose(fid);
fprintf('EEGLAB workflow complete.\n');
exit;
