"""Crop COSEBIs plot: extract column titles + B_n/sigma_n bottom row only."""

from PIL import Image

img = Image.open("images/harmonic_config_cosebis_fiducial.png")
w, h = img.size
print(f"Original: {w}x{h}")

# Title strip: column headers "All scales" / "Fiducial scale cuts"
# Extra padding below to avoid clipping descenders
title_crop = img.crop((0, 0, w, 62))

# Bottom row: B_n/sigma_n panels + x-axis labels
# Start a bit higher to include full y-label
bottom_crop = img.crop((0, 390, w, h))

# Stack vertically
combined_h = title_crop.height + bottom_crop.height
combined = Image.new("RGBA", (w, combined_h), (255, 255, 255, 255))
combined.paste(title_crop, (0, 0))
combined.paste(bottom_crop, (0, title_crop.height))

out = "images/cosebis_bsigma_fiducial.png"
combined.save(out)
print(f"Saved {out} ({w}x{combined_h})")
