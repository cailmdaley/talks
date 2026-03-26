"""Crop PTE heatmap to COSEBIS B_n panel + colorbar only."""

from PIL import Image

img = Image.open("images/config_space_pte_fiducial.png")
w, h = img.size
print(f"Original: {w}x{h}")

# Clean crop: just the COSEBIS panel from its left black frame to end (incl colorbar)
# The divider between xi-B and COSEBIS is at approximately x=1195
# Start just inside the COSEBIS panel frame
crop = img.crop((1255, 0, w, h))

out = "images/pte_cosebis_only.png"
crop.save(out)
print(f"Saved {out} ({crop.width}x{crop.height})")
