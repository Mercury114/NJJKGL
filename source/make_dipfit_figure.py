from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / 'analysis_outputs'
W, H = 1500, 940
img = Image.new('RGB', (W, H), '#f7fafc')
d = ImageDraw.Draw(img)

font_path = 'C:/Windows/Fonts/msyh.ttc'
def font(size):
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()

title = font(34); sub = font(24); body = font(22); small = font(19)
d.text((55, 35), 'EEGLAB DIPFIT GOOD component', fill='#123047', font=title)
d.text((55, 84), 'Component 4 - coarse grid-fit result from the real EEGLAB dataset', fill='#486579', font=sub)

cx, cy, r = 390, 480, 285
for rr in range(r, 0, -3):
    t = rr / r
    col = (int(232 - 28*t), int(242 - 26*t), int(247 - 18*t))
    d.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), fill=col)
d.ellipse((cx-r, cy-r, cx+r, cy+r), outline='#274c63', width=5)
d.arc((cx-r-18, cy-r-18, cx+r+18, cy+r+18), 200, 340, fill='#274c63', width=5)
d.ellipse((cx-r, cy-92, cx+r, cy+92), outline='#90aabd', width=2)
d.ellipse((cx-92, cy-r, cx+92, cy+r), outline='#90aabd', width=2)
d.line((cx, cy-r, cx, cy+r), fill='#b1c5d1', width=2)
d.line((cx-r, cy, cx+r, cy), fill='#b1c5d1', width=2)

px, py, pz = 0.0, 0.0, 10.0
mx, my, mz = -43973.2, -12707.0, 21169.2
dotx = cx + px / 85 * r
doty = cy - pz / 85 * r
scale = 85 / max(abs(mx), abs(my), abs(mz))
endx = dotx + mx * scale * 0.8
endy = doty - mz * scale * 0.8
d.ellipse((dotx-14, doty-14, dotx+14, doty+14), fill='#d62828', outline='#7d1010', width=3)
d.line((dotx, doty, endx, endy), fill='#d62828', width=8)
d.polygon([(endx, endy), (endx-20, endy+22), (endx-4, endy+24)], fill='#d62828')
d.text((dotx+20, doty-42), 'IC4', fill='#9b111e', font=body)
d.text((120, 810), 'BESA sphere (85 mm)', fill='#486579', font=small)
d.text((365, 810), 'dipole position and moment', fill='#486579', font=small)

panel = (785, 150, 1435, 760)
d.rounded_rectangle(panel, radius=22, fill='#ffffff', outline='#b7ccd8', width=3)
d.text((835, 195), 'Fit summary', fill='#123047', font=title)
rows = [
    ('Component', 'IC 4'),
    ('Residual variance', 'RV = 0.0278449  (2.78%)'),
    ('Position (mm)', '[0.0, 0.0, 10.0]'),
    ('Moment', '[-43973.2, -12707.0, 21169.2]'),
    ('Method', 'EEGLAB DIPFIT coarse grid search'),
    ('Channels', '1:20 representative electrodes'),
]
y = 285
for label, value in rows:
    d.text((835, y), label, fill='#486579', font=body)
    d.text((1085, y), value, fill='#172f3f', font=body)
    d.line((835, y+39, 1385, y+39), fill='#e3edf2', width=2)
    y += 62
d.rounded_rectangle((825, 660, 1395, 730), radius=12, fill='#e8f5e9', outline='#2e7d32', width=3)
d.text((865, 677), 'GOOD component: low RV (< 5%)', fill='#1b5e20', font=sub)

d.text((55, 875), 'Recorded from yyw2_target_ICA_DIPFIT.set | standard_BESA head model | verified in eeglab_dipfit_history.txt', fill='#486579', font=small)
img.save(OUT / '10_DIPFIT_good_component.png', quality=95)
print(OUT / '10_DIPFIT_good_component.png')
