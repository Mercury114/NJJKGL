# 本地 EEGLAB 数据集清单

以下数据集由本仓库对应的源码在本地实际生成，完整文件保留在实验工作目录的 `eeglab_octave_outputs/` 中：

- `yyw2_raw.set/.fdt`
- `yyw2_preprocessed_250Hz.set/.fdt`
- `yyw2_target_epochs_clean.set/.fdt`
- `yyw2_nontarget_epochs_clean.set/.fdt`
- `yyw2_target_ICA.set/.fdt`
- `yyw2_target_ICA_DIPFIT.set/.fdt`

由于原始 CNT 和 FDT 文件较大，未上传 GitHub；本仓库保留了对应的处理参数、事件数量、epoch 数量、图表、EEGLAB history、DIPFIT history 和运行日志，可用于核对和复现实验链路。
