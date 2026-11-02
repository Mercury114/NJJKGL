# EEGLAB 脑电分析实验：简君威

本仓库保存《脑机接口概论》EEGLAB 脑电分析实验的源码、图表、运行日志、EEGLAB history、结果汇总和最终实验报告。

## 实验结果摘要

- 原始数据：`yyw2_train.cnt`，64 通道，1000 Hz，4000 个事件
- 预处理：删除 M1/M2、250 Hz 重采样、平均参考、0.1–15 Hz FIR 带通
- 有效 epoch：目标 55/59；非目标 3879/3941
- PO4 差异峰：约 7.62 μV，约 380 ms
- ICA：EEGLAB `runica`，62 个独立成分
- DIPFIT GOOD 成分：IC4，RV=0.0278449（2.78%），位置 `[0, 0, 10] mm`

## 目录

| 目录 | 内容 |
|---|---|
| `source/` | EEGLAB/Octave 脚本、Python 绘图和报告生成脚本、导联文件 |
| `evidence/figures/` | 10 张实验结果图，含 ERP、头皮地形图、ERSP/ITC、ICA 和 DIPFIT |
| `evidence/` | 参数汇总、运行日志、EEGLAB history 和实际运行记录 |
| `report/` | 最终实验报告 DOCX |

## 复现顺序

1. 准备 GNU Octave 11.3.0、EEGLAB 13.6.5b、DIPFIT 2.3 和 FieldTrip-lite。
2. 将原始 `yyw2_train.cnt` 放在工作目录，并运行 `source/run_eeglab_octave.m` 完成导入、预处理、分段和伪迹剔除。
3. 运行 `source/run_eeglab_ica.m` 完成目标 epoch 的 1–30 Hz 处理和 EEGLAB `runica`。
4. 运行 `source/run_eeglab_dipfit.m` 完成前 10 个成分的 DIPFIT 粗网格搜索，并筛选最低 RV 的 GOOD 成分。
5. 使用 `source/make_eeglab_figures.py` 和 `source/make_dipfit_figure.py` 生成图表；报告由 `source/build_report.py` 生成。

原始 CNT、`.fdt` 大型二进制文件、安装包和完整 EEGLAB 软件目录未上传；这些文件保留在本地实验工作目录中。仓库中的日志、history、图表和汇总文件是本次实际运行的证据。
