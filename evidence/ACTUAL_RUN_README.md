# 实际 EEGLAB 运行记录

本目录中的数据集由工作目录中的 EEGLAB 13.6.5b 函数在 GNU Octave 11.3.0 下实际生成，输入文件为上级目录的 `yyw2_train.cnt`。

- `yyw2_raw.set/.fdt`：CNT 导入结果，64 通道，1000 Hz，4000 个事件。
- `yyw2_preprocessed_250Hz.set/.fdt`：移除 M1/M2、平均参考、250 Hz 重采样、0.1–15 Hz 零相位 FIR 滤波。
- `yyw2_target_epochs_clean.set/.fdt`：事件 1，−200–1000 ms，−200–0 ms 基线，150 μV 阈值，保留 55 trials。
- `yyw2_nontarget_epochs_clean.set/.fdt`：事件 2，同样处理，保留 3879 trials。
- `yyw2_target_ICA.set/.fdt`：目标 epoch 经 1–30 Hz 后由 EEGLAB `runica` 分解，62 个独立成分。
- `yyw2_target_ICA_DIPFIT.set/.fdt`：在当前 ICA 数据集上用 DIPFIT 2.3 的 standard_BESA 模型，对前 10 个成分进行 20 通道粗网格搜索；IC4 为最低 RV 成分，RV=0.0278449，位置 `[0 0 10]` mm。
- `eeglab_ica_history.txt`：ICA 数据集的 EEGLAB history。
- `eeglab_dipfit_history.txt`：DIPFIT 的实际 history、搜索范围、RV、偶极子位置和方向。
- 上级目录的 `eeglab_run.log`：导入、预处理、分段和伪迹剔除日志。
- 上级目录的 `eeglab_ica_run.log`、`eeglab_dipfit_run.log`：ICA 与 DIPFIT 的实际运行日志。
