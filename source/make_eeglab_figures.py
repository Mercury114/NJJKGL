from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
from scipy.signal import welch

from run_eeglab_experiment import OUT, compute_time_frequency, load_loc_positions, savefig


BASE = Path(__file__).resolve().parent
EEGOUT = BASE / "eeglab_octave_outputs"
LOC = BASE / "64-channels.loc"


def load_set(name: str):
    from scipy.io import loadmat

    header = loadmat(EEGOUT / f"{name}.set", squeeze_me=True, struct_as_record=False)["EEG"]
    nbchan, pnts, trials = int(header.nbchan), int(header.pnts), int(header.trials)
    fdt = EEGOUT / (str(getattr(header, "datfile", "")) or str(header.data))
    if not fdt.is_absolute():
        fdt = EEGOUT / fdt.name
    data = np.fromfile(fdt, dtype=np.float32).reshape((nbchan, pnts, trials), order="F")
    channels = [str(x.labels) for x in np.atleast_1d(header.chanlocs)]
    return header, data, channels


def main():
    raw_h, raw, raw_channels = load_set("yyw2_raw")
    pre_h, pre, channels = load_set("yyw2_preprocessed_250Hz")
    target_h, target, _ = load_set("yyw2_target_epochs_clean")
    non_h, non, _ = load_set("yyw2_nontarget_epochs_clean")
    ica_h, ica_data, _ = load_set("yyw2_target_ICA")
    sf_raw = float(raw_h.srate)
    sf = float(pre_h.srate)
    times = np.asarray(target_h.times).ravel() / 1000.0
    display = ["FP1", "Cz", "PO4", "Oz"]
    raw_inds = [raw_channels.index(x) for x in display]
    pre_inds = [channels.index(x) for x in display]
    raw_start, raw_stop = int(21 * sf_raw), int(26 * sf_raw)
    pre_start, pre_stop = int(21 * sf), int(26 * sf)
    raw_preview = raw[raw_inds, raw_start:raw_stop, 0] * 1e-6
    pre_preview = pre[pre_inds, pre_start:pre_stop, 0] * 1e-6
    raw_times = np.arange(raw_preview.shape[1]) / sf_raw + 21
    pre_times = np.arange(pre_preview.shape[1]) / sf + 21

    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    offsets = np.arange(4) * 90
    for i, ch in enumerate(display):
        axes[0].plot(raw_times, raw_preview[i] * 1e6 + offsets[i], lw=0.45, label=ch)
        axes[1].plot(pre_times, pre_preview[i] * 1e6 + offsets[i], lw=0.7, label=ch)
    axes[0].set_title("Real EEGLAB CNT import (1000 Hz, before preprocessing)")
    axes[1].set_title("Real EEGLAB output after M1/M2 removal, resampling, average reference and 0.1-15 Hz FIR")
    for ax in axes:
        ax.set_ylabel("Amplitude + offset (uV)")
        ax.grid(alpha=0.2)
        ax.legend(ncol=4, loc="upper right")
    axes[0].set_xlabel("Time (s)")
    axes[1].set_xlabel("Time (s)")
    fig.tight_layout()
    savefig("01_import_and_preprocessing.png")

    # Quality distribution for the retained EEGLAB epochs and PSD of real EEGLAB data.
    target_ptp = np.ptp(target, axis=1).max(axis=0)
    non_ptp = np.ptp(non, axis=1).max(axis=0)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].hist(np.r_[target_ptp, non_ptp], bins=60, color="#557a95", alpha=0.9)
    axes[0].axvline(150, color="#c0392b", lw=2, label="threshold = 150 uV")
    axes[0].set_title("Peak-to-peak amplitude of retained EEGLAB epochs")
    axes[0].set_xlabel("Maximum channel PTP (uV)")
    axes[0].set_ylabel("Number of retained epochs")
    axes[0].legend()
    po4_pre = pre[channels.index("PO4"), :, 0] * 1e-6
    f0, p0 = welch(raw[raw_channels.index("PO4"), raw_start:raw_stop, 0] * 1e-6, fs=sf_raw, nperseg=4096)
    f1, p1 = welch(po4_pre[pre_start:pre_stop], fs=sf, nperseg=512)
    axes[1].semilogy(f0, p0, label="Before preprocessing")
    axes[1].semilogy(f1, p1, label="After preprocessing")
    axes[1].set_xlim(0, 45)
    axes[1].set_title("PO4 PSD from real EEGLAB datasets")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("PSD (V^2/Hz)")
    axes[1].grid(alpha=0.2)
    axes[1].legend()
    fig.tight_layout()
    savefig("02_epoch_quality_and_psd.png")

    po4 = channels.index("PO4")
    # EEGLAB CNT import stores the signal in microvolts in these .fdt files.
    po4_target = target[po4].T
    po4_non = non[po4].T
    erp_target = target.mean(axis=2)
    erp_non = non.mean(axis=2)
    erp_diff = erp_target - erp_non
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for values, color, label in [(po4_target, "#d35400", "Target"), (po4_non, "#2874a6", "Non-target")]:
        mean = values.mean(axis=0)
        sem = values.std(axis=0, ddof=1) / np.sqrt(values.shape[0])
        ax.plot(times * 1000, mean, color=color, lw=2, label=label)
        ax.fill_between(times * 1000, mean - sem, mean + sem, color=color, alpha=0.15)
    ax.plot(times * 1000, erp_diff[po4], color="#2e8b57", lw=2, label="Target - non-target")
    ax.axvline(0, color="k", lw=0.8)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("PO4 ERP comparison from real EEGLAB epochs")
    ax.set_xlabel("Time relative to event (ms)")
    ax.set_ylabel("Amplitude (uV)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    fig.tight_layout()
    savefig("03_PO4_ERP_target_nontarget_difference.png")

    positions = load_loc_positions(LOC, channels)
    topo_times = [0.3, 0.4, 0.5]
    topo_inds = [int(round((t - times[0]) * sf)) for t in topo_times]
    from run_eeglab_experiment import plot_topo_grid

    plot_topo_grid([erp_target[:, i] for i in topo_inds], [f"Target {int(t * 1000)} ms" for t in topo_times], positions, channels, "04_target_scalp_maps_300_400_500ms.png")
    plot_topo_grid([erp_non[:, i] for i in topo_inds], [f"Non-target {int(t * 1000)} ms" for t in topo_times], positions, channels, "05_nontarget_scalp_maps_300_400_500ms.png")
    plot_topo_grid([erp_diff[:, i] for i in topo_inds], [f"Difference {int(t * 1000)} ms" for t in topo_times], positions, channels, "06_difference_scalp_maps_300_400_500ms.png")

    freqs = np.linspace(2.0, 30.0, 29)
    tf_times, target_ersp, target_itc = compute_time_frequency(target.transpose(2, 0, 1), po4, sf, freqs)
    _, non_ersp, non_itc = compute_time_frequency(non.transpose(2, 0, 1), po4, sf, freqs)
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), gridspec_kw={"width_ratios": [1, 1, 0.8]})
    for row, label, ersp, itc, erp in [(0, "Target", target_ersp, target_itc, erp_target), (1, "Non-target", non_ersp, non_itc, erp_non)]:
        im0 = axes[row, 0].pcolormesh(tf_times * 1000, freqs, ersp, shading="auto", cmap="RdBu_r", vmin=-3, vmax=3)
        im1 = axes[row, 1].pcolormesh(tf_times * 1000, freqs, itc, shading="auto", cmap="viridis", vmin=0, vmax=1)
        axes[row, 0].set_title(f"{label} ERSP (dB)")
        axes[row, 1].set_title(f"{label} ITC")
        axes[row, 2].plot(times * 1000, erp[po4], color="#c0392b" if row == 0 else "#2874a6")
        axes[row, 2].set_title(f"{label} PO4 ERP")
        for col in [0, 1]:
            axes[row, col].set_ylabel("Frequency (Hz)")
            axes[row, col].set_xlabel("Time (ms)")
            axes[row, col].axvline(0, color="k", lw=0.7)
        axes[row, 2].set_xlabel("Time (ms)")
        axes[row, 2].set_ylabel("uV")
    fig.colorbar(im0, ax=axes[:, 0], shrink=0.75, label="dB")
    fig.colorbar(im1, ax=axes[:, 1], shrink=0.75, label="ITC")
    fig.suptitle("PO4 time-frequency analysis from real EEGLAB epochs (baseline: -200 to 0 ms)", fontsize=14)
    fig.tight_layout()
    savefig("07_PO4_time_frequency_ERSP_ITC.png")

    icawinv = np.asarray(ica_h.icawinv)
    n_show = min(12, icawinv.shape[1])
    fig, axes = plt.subplots(3, 4, figsize=(13, 10))
    for i, ax in enumerate(axes.flat):
        if i >= n_show:
            ax.axis("off")
            continue
        val = icawinv[:, i]
        lim = max(float(np.max(np.abs(val))), 1e-9)
        mne.viz.plot_topomap(val, positions, axes=ax, cmap="RdBu_r", vlim=(-lim, lim), contours=5, sensors=True, outlines="head", sphere=(0, 0, 0, 0.6), show=False)
        ax.set_title(f"IC {i + 1}")
    fig.suptitle("ICA component scalp maps from real EEGLAB runica (62 components)", fontsize=14)
    fig.tight_layout()
    savefig("08_ICA_component_topographies.png")

    w = np.asarray(ica_h.icaweights) @ np.asarray(ica_h.icasphere)
    source = np.einsum("ij,jkt->ikt", w, ica_data)
    fig, ax = plt.subplots(figsize=(10, 5))
    for i in range(min(6, source.shape[0])):
        ax.plot(times * 1000, source[i].mean(axis=1), lw=1.3, label=f"IC {i + 1}")
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Average ICA component waveforms from real EEGLAB runica")
    ax.set_xlabel("Time relative to event (ms)")
    ax.set_ylabel("Component amplitude (a.u.)")
    ax.grid(alpha=0.2)
    ax.legend(ncol=3, frameon=False)
    fig.tight_layout()
    savefig("09_ICA_component_ERP_waveforms.png")


if __name__ == "__main__":
    main()
