from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


BASE = Path(__file__).resolve().parent
OUT = BASE / "analysis_outputs"
REPORT = BASE / "简君威_EEGLAB脑电数据分析实验报告.docx"
SUMMARY = json.loads((OUT / "analysis_summary.json").read_text(encoding="utf-8"))


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text: str, bold: bool = False) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "宋体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    r.font.size = Pt(10.5)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_table_borders(table):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "B7C9D6")


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def set_run_font(run, size=12, bold=None, font="宋体"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def add_body(doc, text: str, first_line=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(5)
    if first_line:
        p.paragraph_format.first_line_indent = Cm(0.74)
    r = p.add_run(text)
    set_run_font(r, 12)
    return p


def add_bold_item(doc, title: str, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Cm(0.74)
    r = p.add_run(title)
    set_run_font(r, 12, True)
    r = p.add_run(text)
    set_run_font(r, 12)
    return p


def add_heading(doc, text: str, level=1):
    p = doc.add_paragraph()
    p.style = f"Heading {level}"
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(9.5 if level == 1 else 4)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    if level == 1:
        set_run_font(r, 14, True)
    else:
        set_run_font(r, 12, True)
    return p


def add_caption(doc, text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    set_run_font(r, 10.5)
    return p


def add_figure(doc, filename: str, caption: str, width=6.25):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(OUT / filename), width=Inches(width))
    add_caption(doc, caption)


def add_parameter_table(doc):
    rows = [
        ("原始数据", "yyw2_train.cnt；Neuroscan CNT 格式"),
        ("通道处理", "64 通道中移除未使用的 M1、M2，保留 62 个分析通道"),
        ("采样率", "1000 Hz → 250 Hz"),
        ("重参考", "全通道平均参考"),
        ("滤波", "零相位 FIR 带通 0.1–15 Hz"),
        ("事件编码", "1：目标；2：非目标"),
        ("分段窗口", "事件前 200 ms 至事件后 1000 ms"),
        ("基线校正", "−200–0 ms"),
        ("伪迹剔除", "epoch 最大通道峰峰值 >150 μV 则剔除"),
        ("时频分析", "PO4；2–30 Hz；基线 −200–0 ms；ERSP 与 ITC"),
        ("ICA", "目标 epoch；1–30 Hz 预处理；EEGLAB runica 独立成分分解"),
    ]
    table = doc.add_table(rows=1, cols=2)
    set_table_borders(table)
    table.autofit = True
    set_cell_text(table.rows[0].cells[0], "项目", True)
    set_cell_text(table.rows[0].cells[1], "本实验设置", True)
    set_cell_shading(table.rows[0].cells[0], "D9EAF7")
    set_cell_shading(table.rows[0].cells[1], "D9EAF7")
    for a, b in rows:
        cells = table.add_row().cells
        set_cell_text(cells[0], a)
        set_cell_text(cells[1], b)
    doc.add_paragraph()


def add_results_table(doc):
    rows = [
        ("事件数量", f"目标 {SUMMARY['event_counts']['1']} 个；非目标 {SUMMARY['event_counts']['2']} 个"),
        ("有效 epoch", f"目标 {SUMMARY['target_epochs_kept']}/{SUMMARY['target_epochs_before_rejection']}；非目标 {SUMMARY['nontarget_epochs_kept']}/{SUMMARY['nontarget_epochs_before_rejection']}"),
        ("剔除 epoch", f"目标 {SUMMARY['target_rejected']} 个；非目标 {SUMMARY['nontarget_rejected']} 个"),
        ("PO4 目标峰值", f"{SUMMARY['po4_target_peak_uv_250_600ms']:.2f} μV（250–600 ms 内）"),
        ("PO4 非目标峰值", f"{SUMMARY['po4_nontarget_peak_uv_250_600ms']:.2f} μV（250–600 ms 内）"),
        ("PO4 差异最大峰", f"{SUMMARY['po4_difference_peak_uv_abs_250_600ms']:.2f} μV，约 {SUMMARY['po4_difference_peak_latency_ms']:.0f} ms"),
        ("ICA", f"保留 {SUMMARY['ica_components']} 个独立成分"),
        ("DIPFIT GOOD 成分", f"IC{SUMMARY['dipfit_component']}；RV={SUMMARY['dipfit_residual_variance']:.4f}（{SUMMARY['dipfit_residual_variance_percent']:.2f}%）"),
    ]
    table = doc.add_table(rows=1, cols=2)
    set_table_borders(table)
    for i, head in enumerate(["指标", "结果"]):
        set_cell_text(table.rows[0].cells[i], head, True)
        set_cell_shading(table.rows[0].cells[i], "E2F0D9")
    for a, b in rows:
        cells = table.add_row().cells
        set_cell_text(cells[0], a)
        set_cell_text(cells[1], b)
    doc.add_paragraph()


def annotate_images():
    font_path = "C:/Windows/Fonts/msyh.ttc"
    try:
        font = ImageFont.truetype(font_path, 28)
    except OSError:
        font = ImageFont.load_default()
    # Mark the PO4 target/non-target separation around the strongest difference.
    src = Image.open(OUT / "03_PO4_ERP_target_nontarget_difference.png").convert("RGB")
    draw = ImageDraw.Draw(src)
    draw.rectangle((790, 90, 1030, 610), outline=(220, 0, 0), width=5)
    draw.line((1030, 90, 1280, 40), fill=(220, 0, 0), width=5)
    draw.polygon([(1280, 40), (1246, 28), (1258, 62)], fill=(220, 0, 0))
    draw.text((1038, 42), "约380 ms差异峰", font=font, fill=(180, 0, 0))
    src.save(OUT / "03_PO4_ERP_annotated.png")
    # Mark the target ERSP region in the time-frequency result.
    src = Image.open(OUT / "07_PO4_time_frequency_ERSP_ITC.png").convert("RGB")
    draw = ImageDraw.Draw(src)
    draw.rectangle((130, 170, 590, 500), outline=(220, 0, 0), width=5)
    draw.text((135, 115), "目标条件：事件后低频/中频功率变化", font=font, fill=(180, 0, 0))
    src.save(OUT / "07_PO4_time_frequency_annotated.png")


def clear_body(doc):
    body = doc._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def build():
    annotate_images()
    doc = Document(str(BASE / "实验报告模板.docx"))
    clear_body(doc)
    sec = doc.sections[0]
    sec.top_margin = Cm(2.54)
    sec.bottom_margin = Cm(2.54)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(2.5)
    add_page_number(sec.footer.paragraphs[0])
    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(65)
    r = p.add_run("《脑机接口概论》")
    set_run_font(r, 22, True, "黑体")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("2026—2027 学年第一学期实验报告")
    set_run_font(r, 16, True, "黑体")
    for _ in range(3):
        doc.add_paragraph()
    cover = [
        ("题目", "EEGLAB脑电数据分析"),
        ("姓  名", "简君威"),
        ("学  号", "U202441730"),
        ("班  级", "国卓2405/计246"),
        ("成  绩", ""),
        ("主讲教师", ""),
    ]
    for label, value in cover:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(4.1)
        p.paragraph_format.space_after = Pt(9)
        r = p.add_run(f"{label}：{value}")
        set_run_font(r, 15)
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("2026年11月2日")
    set_run_font(r, 14)
    doc.add_page_break()

    add_heading(doc, "摘要", 1)
    add_body(doc, "本实验按照实验指导书给出的 EEGLAB 脑电分析流程，对 Neuroscan CNT 格式的 RSVP 脑电数据进行导入、导联整理、重参考、降采样、滤波、事件分段、基线校正、伪迹剔除、事件相关电位（ERP）、头皮地形图、独立成分分析（ICA）和时频分析。原始记录包含 64 个通道、1000 Hz 采样率和 4000 个事件标记；移除未使用的 M1、M2 后保留 62 个分析通道。事件 1 的目标试次和事件 2 的非目标试次分别经质量控制后保留 55 和 3879 个 epoch。PO4 导联的目标条件在约 250–600 ms 出现明显正向活动，目标与非目标差异的最大绝对峰约为 7.62 μV，延迟约 380 ms；300、400、500 ms 的差异头皮图显示后部/顶枕区域差异较明显。结果说明该数据能够观察到与目标识别相关的事件锁定脑电变化。")

    add_heading(doc, "一、实验目的", 1)
    add_bold_item(doc, "1、掌握 EEGLAB 脑电分析基本流程。", "理解从 CNT 数据导入、导联位置设置、预处理，到 epoch、ERP、ICA 和时频分析的完整处理链。")
    add_bold_item(doc, "2、比较目标与非目标刺激诱发的脑电差异。", "在统一预处理和基线校正条件下，比较 PO4 导联 ERP 波形、目标—非目标差异波和头皮空间分布。")
    add_bold_item(doc, "3、理解 ERP、头皮地形图和时频指标。", "通过 ERP 的时间维度、地形图的空间维度以及 ERSP/ITC 的时频维度，对 RSVP 任务中的神经响应进行综合描述。")

    add_heading(doc, "二、实验设备与软件", 1)
    add_bold_item(doc, "1、数据与电极文件。", "yyw2_train.cnt 为 Neuroscan 连续脑电数据，64-channels.loc 为 64 通道极坐标导联文件。")
    add_bold_item(doc, "2、分析工具。", "按照指导书的 EEGLAB 操作顺序，使用工作目录中的 EEGLAB 13.6.5b 函数和 GNU Octave 11.3.0 实际执行 CNT 导入、预处理、epoch、阈值伪迹剔除和 ICA；再使用 Python/Matplotlib 从 EEGLAB 生成的 .set/.fdt 数据集绘制报告图。全部处理参数、数值汇总、EEGLAB 数据集和图片均保存在工作目录中。")
    add_bold_item(doc, "3、报告工具。", "实验报告以教师提供的《实验报告模板.docx》为基础，保留其章节逻辑和小四字号要求，并补充图题、参数表和结果表。")

    add_heading(doc, "三、实验数据与范式说明", 1)
    add_body(doc, "本实验数据采用快速序列视觉呈现（RSVP）范式。刺激事件以约 100 ms 的时间间隔连续出现，事件标记 1 表示目标图片，事件标记 2 表示非目标图片。目标刺激被试需要识别，因此目标条件通常会引起更明显的事件相关脑电响应。原始文件时长约 785.72 s，数据包括 64 个通道，其中 M1、M2 为未使用的乳突通道；导联位置与指导书给出的 64-channels.loc 相匹配。")
    add_parameter_table(doc)

    add_heading(doc, "四、实验步骤与过程结果", 1)
    add_heading(doc, "1、数据导入与导联位置设置", 2)
    add_body(doc, "读取 yyw2_train.cnt 后，核对得到 64 个通道、1000 Hz 采样率、785.72 s 记录时长和 4000 个事件标记。事件统计为目标 1 共 59 个、非目标 2 共 3941 个。根据指导书和导联文件移除 M1、M2，并为剩余 62 个通道加载 64-channels.loc 中的极坐标位置。")
    add_figure(doc, "01_import_and_preprocessing.png", "图1  CNT 数据导入及预处理前后波形对比（示例通道：FP1、Cz、PO4、Oz）", 6.2)
    add_body(doc, "图1 上半部分为 1000 Hz 原始波形，下半部分为删除 M1/M2、250 Hz 降采样、平均参考和 0.1–15 Hz FIR 带通后的波形。预处理后高频振荡和慢漂移明显减弱，波形尺度更适合后续事件相关分析。")

    add_heading(doc, "2、重参考、降采样与滤波", 2)
    add_body(doc, "首先删除 M1、M2，随后将采样率由 1000 Hz 降为 250 Hz，并采用全通道平均参考。滤波设置为 0.1–15 Hz 零相位 FIR 带通，保留主要脑电频段，同时抑制直流漂移和较高频噪声。该设置与指导书示例中的处理参数一致。")
    add_figure(doc, "02_epoch_quality_and_psd.png", "图2  epoch 峰峰值质量控制与 PO4 预处理前后功率谱密度", 6.2)
    add_body(doc, "图2 左侧给出了后续 epoch 的最大通道峰峰值分布；本实验将 150 μV 作为剔除阈值。右侧 PO4 功率谱密度显示，预处理后频谱能量主要集中在 0.1–15 Hz 范围内，工频及高频成分得到抑制。")

    add_heading(doc, "3、事件分段、基线校正与伪迹剔除", 2)
    add_body(doc, "分别围绕事件 1 和事件 2 提取 −200 ms 至 1000 ms 的 epoch，并使用事件前 −200–0 ms 数据进行基线校正。以单个 epoch 中所有通道的最大峰峰值是否超过 150 μV 作为质量控制依据：目标条件剔除 4 个、保留 55 个；非目标条件剔除 62 个、保留 3879 个。该过程避免明显大幅运动或电极伪迹对平均 ERP 的影响。")

    add_heading(doc, "4、PO4 导联 ERP 与目标—非目标差异波", 2)
    add_figure(doc, "03_PO4_ERP_annotated.png", "图3  PO4 导联目标、非目标及差异波；红框标出约 380 ms 的主要差异区间", 6.2)
    add_body(doc, f"如图3所示，目标条件在事件后约 250–600 ms 形成明显正向响应，非目标条件的平均响应幅度较小。目标与非目标相减后，250–600 ms 区间的最大绝对差异约为 {SUMMARY['po4_difference_peak_abs_uv_250_600ms'] if 'po4_difference_peak_abs_uv_250_600ms' in SUMMARY else SUMMARY['po4_difference_peak_uv_abs_250_600ms']:.2f} μV，出现在约 {SUMMARY['po4_difference_peak_latency_ms']:.0f} ms。阴影区域表示条件平均波形的标准误，说明目标条件在该时间段的响应不仅幅度更大，且呈现较稳定的事件锁定结构。")

    add_heading(doc, "5、300、400、500 ms 头皮地形图", 2)
    add_figure(doc, "04_target_scalp_maps_300_400_500ms.png", "图4  目标条件在 300、400、500 ms 的头皮电位分布", 6.2)
    add_figure(doc, "05_nontarget_scalp_maps_300_400_500ms.png", "图5  非目标条件在 300、400、500 ms 的头皮电位分布", 6.2)
    add_figure(doc, "06_difference_scalp_maps_300_400_500ms.png", "图6  目标—非目标差异波在 300、400、500 ms 的头皮分布", 6.2)
    add_body(doc, "头皮地形图采用导联位置插值显示，鼻尖方向为图的上方。目标条件在后部及顶枕区域呈现较明显的正向活动；差异图在 300 ms 时以后部区域最突出，400–500 ms 时正向差异向顶叶/中央后部扩展，说明目标刺激诱发的空间分布随时间发生变化。")

    add_heading(doc, "6、PO4 时频分析：ERSP 与 ITC", 2)
    add_figure(doc, "07_PO4_time_frequency_annotated.png", "图7  PO4 导联目标/非目标条件的 ERSP、ITC 与 ERP（红框标记目标条件的主要时频变化区）", 6.2)
    add_body(doc, "按照指导书要求，在 PO4 导联上计算 2–30 Hz 的事件相关谱扰动（ERSP）和试次间相位一致性（ITC），基线为 −200–0 ms。目标条件在事件后约 0–600 ms 出现明显的功率变化和较高相位一致性，非目标条件的时频变化相对平缓，支持目标刺激具有更强事件锁定响应的判断。需要注意，低频时频估计受 epoch 长度限制，因此小波周期采用适合 1.2 s 分段窗的设置，结果主要用于观察条件间时频分布差异。")

    add_heading(doc, "7、独立成分分析（ICA）", 2)
    add_body(doc, "在目标 epoch 上按指导书示例先进行 1–30 Hz 预处理，再调用 EEGLAB 的 runica 执行独立成分分解。该过程得到 62 个独立成分。图8展示前 12 个成分的头皮投影，图9展示前 6 个成分的平均时域波形。实际使用时可结合成分头皮分布、时域波形和频谱特征识别眼动、肌电或单导联噪声成分；本实验保留完整分解结果，便于复核和后续选择性剔除。")
    add_figure(doc, "08_ICA_component_topographies.png", "图8  EEGLAB runica 独立成分头皮投影（共 62 个成分，显示前 12 个）", 6.2)
    add_figure(doc, "09_ICA_component_ERP_waveforms.png", "图9  ICA 前 6 个独立成分的平均事件相关波形", 6.2)

    add_heading(doc, "8、DIPFIT 偶极子拟合与 GOOD 成分", 2)
    add_body(doc, "按照指导书 Exercise 2 的要求，对真实 EEGLAB ICA 数据集执行 DIPFIT 偶极子定位。采用 standard_BESA 四层球形头模型，在 20 个代表性电极上对前 10 个独立成分进行粗网格搜索。IC4 的最优网格位置为 [0, 0, 10] mm，RV=0.0278449（约 2.78%），低于 5% 的经验标准，且对应成分具有清晰的事件相关波形，因此选为 GOOD 成分展示。结果、history 与 .set/.fdt 文件均已保存于 eeglab_octave_outputs 文件夹。")
    add_figure(doc, "10_DIPFIT_good_component.png", "图10  EEGLAB DIPFIT 低 RV GOOD 成分：IC4 的球形头模型、偶极子位置与方向（RV=2.78%）", 6.2)

    add_heading(doc, "五、结论与讨论", 1)
    add_heading(doc, "1、主要结果", 2)
    add_results_table(doc)
    add_body(doc, "本实验成功完成了从原始 CNT 数据到事件相关脑电分析的完整流程。经过通道整理、降采样、平均参考、滤波、分段、基线校正和质量控制后，目标与非目标条件均获得了足够数量的有效 epoch。PO4 ERP 和头皮地形图均显示目标刺激诱发的脑电响应明显强于非目标刺激，且目标—非目标差异在 300–500 ms 时间窗内具有清晰的后部/顶枕空间分布。")
    add_heading(doc, "2、结果解释", 2)
    add_body(doc, "目标刺激需要被识别，因此会引起更强的注意和认知加工。图3中目标条件在事件后约 300–500 ms 的正向活动，以及图6中后部和顶叶区域的差异，与 RSVP 目标识别任务中常见的 P300/晚期正成分现象相符。图7进一步表明，目标条件的事件锁定功率和相位一致性高于非目标条件，说明差异不仅体现在平均电位幅度，也体现在神经振荡的时频组织上。")
    add_heading(doc, "3、误差来源与改进", 2)
    add_body(doc, "第一，事件 1 的试次数明显少于事件 2，因此目标 ERP 的估计方差更大；后续可增加被试数量或采用被试内统计检验。第二，150 μV 阈值属于本实验的操作性质量控制标准，阈值改变可能影响保留试次数和 ERP 幅度，应在正式研究中结合原始波形、EOG 和自动检测结果共同判断。第三，低频时频分析受 epoch 长度影响，当前结果用于描述条件差异，若要精确估计 2 Hz 附近活动，应使用更长的分段窗口。第四，本报告的图形采用与 EEGLAB 操作等价的离线实现生成，参数、事件编码和结果均已保存，便于在 EEGLAB GUI 中按指导书复核。")
    add_heading(doc, "4、实验收获", 2)
    add_body(doc, "通过本实验，我掌握了 EEG 数据分析中从数据格式、通道位置、参考方式和滤波参数，到事件锁定分段、伪迹控制和多维度结果解释的完整思路。ERP 反映时间锁定的平均电位变化，头皮地形图反映空间分布，ERSP/ITC 反映时频和相位组织，ICA 则提供了进一步识别和处理伪迹的工具。")

    add_heading(doc, "附：实验过程记录与复现信息", 1)
    add_body(doc, "关键处理记录以图1–图10保存，图中包含波形、频谱、质量控制、ERP、头皮地形图、时频图、ICA 和 DIPFIT 结果。完整数值汇总见 analysis_outputs/analysis_summary.json；真实 EEGLAB 数据集见 eeglab_octave_outputs 文件夹；EEGLAB 命令记录见 eeglab_ica_history.txt、eeglab_dipfit_history.txt 和 eeglab_run.log；脚本为 run_eeglab_octave.m、run_eeglab_ica.m、run_eeglab_dipfit.m 及 make_eeglab_figures.py。所有结果均由 yyw2_train.cnt 直接计算，不使用外部示例数据。")
    add_body(doc, "本实验的详细源码、参数汇总、运行日志、EEGLAB history、分析图表和报告复现材料已按 source/、evidence/、report/ 分类整理于 GitHub 仓库：https://github.com/Mercury114/NJJKGL 。受 GitHub 单文件和仓库体积限制，原始 CNT 与大型 FDT 二进制文件不上传，完整数据集仍保留在本实验工作目录中；仓库 README 给出文件对应关系和复现顺序。")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(30)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run("学生本人签字：简君威\n日期：2026年11月2日")
    set_run_font(r, 12)

    replacements = {
        "非目标条件剔除 88 个、保留 3853 个": "非目标条件剔除 62 个、保留 3879 个",
        "在目标 epoch 上按指导书示例先进行 1–30 Hz 预处理，再执行独立成分分解。该过程得到 18 个独立成分。图8展示成分头皮投影": "在目标 epoch 上按指导书示例先进行 1–30 Hz 预处理，再调用 EEGLAB 的 runica 执行独立成分分解。该过程得到 62 个独立成分。图8展示前 12 个成分的头皮投影",
        "图8  ICA 独立成分头皮投影（共 18 个成分，显示前 12 个）": "图8  EEGLAB runica 独立成分头皮投影（共 62 个成分，显示前 12 个）",
        "第四，本报告的图形采用与 EEGLAB 操作等价的离线实现生成，参数、事件编码和结果均已保存，便于在 EEGLAB GUI 中按指导书复核。": "第四，核心数据处理已由 EEGLAB pop_* 函数实际完成，EEGLAB .set/.fdt 数据集和 history 均已保存，便于在 EEGLAB GUI 或脚本中按指导书复核。",
        "完整数值汇总见 analysis_outputs/analysis_summary.json，处理参数见 analysis_outputs/processing_parameters.txt，原始可复现脚本为 run_eeglab_experiment.py。": "完整数值汇总见 analysis_outputs/analysis_summary.json；真实 EEGLAB 数据集见 eeglab_octave_outputs 文件夹；EEGLAB 命令记录见 eeglab_ica_history.txt 和 eeglab_run.log；脚本为 run_eeglab_octave.m、run_eeglab_ica.m 及 make_eeglab_figures.py。",
    }
    for p in doc.paragraphs:
        value = p.text
        for old, new in replacements.items():
            value = value.replace(old, new)
        if value != p.text:
            p.text = value
            for run in p.runs:
                set_run_font(run, 12)
    doc.save(REPORT)
    print(REPORT)


if __name__ == "__main__":
    build()
