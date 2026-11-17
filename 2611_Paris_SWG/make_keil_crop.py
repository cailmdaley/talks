"""The Omega_m and A_s corner of F. Keil's Flagship-2 blinding test (images/paris_keil_fs2_2x2pt_blinding.png):
its top-left two rows, the legend moved beside them, and the tick labels of the two columns from the bottom
of the full plot. Pixels are copied, nothing is redrawn.

Run in the cmbx container: app python make_keil_crop.py
"""
import os
from PIL import Image

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
src = Image.open(os.path.join(IMG, "paris_keil_fs2_2x2pt_blinding.png")).convert("RGB")
panels = src.crop((39, 35, 640, 530))        # Omega_m 1-D; A_s against Omega_m and A_s 1-D
ticks = src.crop((39, 1246, 640, 1346))      # the tick labels and axis names under those two columns
legend = src.crop((740, 35, 1350, 272))
out = Image.new("RGB", (990, panels.height + ticks.height), "white")
out.paste(panels, (0, 0))
out.paste(ticks, (0, panels.height))
out.paste(legend, (372, 0))
out.save(os.path.join(IMG, "paris_keil_fs2_blinding_om_as.png"))
print(out.size)
