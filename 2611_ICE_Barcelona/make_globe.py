# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "pillow", "healpy", "mocpy", "astropy", "imageio-ffmpeg"]
# ///
"""The survey globe on slide `unions-north`: Stage III lensing footprints, then UNIONS and Euclid DR1.

An orthographic sky globe (inside view, RA increasing to the left) over the
Gaia EDR3 colour map. The camera holds on the southern Stage III surveys,
travels north to the UNIONS cap, circles it once (the view axis precesses
about the cap's centre, showing its north, east, south and west edges) and
settles on a held view of UNIONS and Euclid DR1.

Layers, bottom to top, each a translucent fill with a solid edge:
  DES        des.fits, the DES wide-survey envelope (MOC, 5,155 deg²)
  KiDS       kids.fits, the KiDS-N/S science-quality mask (MOC, 891 deg²)
  HSC        hsc_y3.npz, the six HSC Y3 shear fields (digitised, 572 deg² gross)
  UNIONS v2  the 22,901 DR6 tiles in the v2 shape catalog (tile coverage, before
             star masks; the masked catalog covers 5,223 deg²), light orange
  UNIONS-3500  the first-release shear footprint (nside 4096 mask, 2,894 deg²), deep orange
  Euclid DR1 the observed DR1 VIS footprint, violet
and the final UNIONS footprint (all 23,114 DR6 tiles) as an orange line.

Inputs:
  --footprints  the ADE talk's `figures/data/footprints` (DES, KiDS, HSC, DR6 status;
                provenance in its README)
  --u3500       mask_map_footprint_nside_4096.fits, the UNIONS-3500 footprint
  --gaia        gaia_edr3_colour_equirectangular.png (ESA/Gaia/DPAC, CC BY-SA 3.0 IGO)
  --font        Helvetica.ttc (macOS system font; copied along to render elsewhere)
  --old-video   the ADE talk's media/globe_surveys.mp4, from which the Euclid DR1
                footprint is recovered (see `euclid_dr1`): the DR1 MOC itself is an
                internal product kept off this laptop. The recovered raster stays in
                --cache and is never committed.

    uv run 2611_ICE_Barcelona/make_globe.py [--jobs 8] [--frames 0,200,515]

The full render (516 frames) runs on a Colab CPU VM, not the laptop: tar this script into
talks/2611_ICE_Barcelona/ beside talks/images/, with the DES/KiDS/HSC/DR6-status footprint
files, the Gaia PNG, Helvetica.ttc and the cached globe_masks.npz under in/, then
    colab new -s globe --high-mem && colab upload -s globe globe.tgz /content/globe.tgz
    colab ssh -s globe -- 'cd /content && tar xzf globe.tgz && pip install uv && cd talks &&
        uv run 2611_ICE_Barcelona/make_globe.py --footprints ../in/footprints --gaia ../in/gaia.png
        --cache ../in/cache --font ../in/Helvetica.ttc --jobs $(nproc)'
    colab download -s globe /content/talks/images/unions_globe_surveys.mp4 ...; colab stop -s globe

Writes images/unions_globe_surveys.mp4 and its poster images/unions_globe_surveys.jpg
(the last frame); --frames writes those frames as PNGs to --cache instead.
"""
import argparse
import json
import math
import multiprocessing as mp
import subprocess
from pathlib import Path

import healpy as hp
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

HERE = Path(__file__).parent
IMAGES = HERE.parent / "images"
HOME = Path.home()

S, SS, FPS = 1080, 2, 30            # frame side (px), supersampling, frame rate
CX = CY = S / 2
R = 508                             # globe radius (px), as in the ADE video
NS = 1024                           # HEALPix resolution of the footprint masks
GROUND = (246, 240, 228)            # the aquarelle slide ground

# fills (RGB, opacity) and edge colours
DES = ((92, 132, 190), .42)
KIDS = ((52, 178, 140), .50)
HSC = ((222, 186, 62), .50)
V2 = ((255, 196, 140), .72)
U3500 = ((196, 64, 18), .9)
DR1 = ((166, 128, 230), .55)
FINAL = (238, 112, 40)

SOUTH = (30.0, -30.0)               # the opening view (RA, Dec of the globe centre)
HOLD = (185.0, 57.0)                # the held view on UNIONS and Euclid DR1
CONE = 26.0                         # precession half-angle (deg)
# timeline (s): hold south, travel north, precess, settle and hold
T_SOUTH, T_TRAVEL, T_PRECESS, T_HOLD = 1.2, 4.0, 9.0, 3.0

LABELS = [  # text, RA, Dec, colour
    ("DES", 34.6, -15.7, (150, 185, 235)),
    ("KiDS", 200, -1.5, (110, 225, 185)),
    ("KiDS", 15, -31, (110, 225, 185)),
    ("HSC", 225, 1.5, (245, 210, 100)),
    ("Euclid DR1", 70, -44.4, (200, 175, 250)),
    ("Euclid DR1", 215, 74, (200, 175, 250)),
    ("UNIONS-3500", 208, 50, (255, 150, 100)),
    ("UNIONS v2", 145, 54, (255, 214, 175)),
]

EQ2GAL = np.array([[-0.0548755604, -0.8734370902, -0.4838350155],
                   [0.4941094279, -0.4448296300, 0.7469822445],
                   [-0.8676661490, -0.1980763734, 0.4559837762]])


def unit(ra, dec):
    a, d = np.radians(ra), np.radians(dec)
    return np.stack([np.cos(d) * np.cos(a), np.cos(d) * np.sin(a), np.sin(d)], -1)


def radec(v):
    return np.degrees(np.arctan2(v[..., 1], v[..., 0])) % 360, np.degrees(np.arcsin(np.clip(v[..., 2], -1, 1)))


def basis(ra, dec, roll=0.0):
    """View direction c, screen-right r, screen-up u for a camera centred on (ra, dec)."""
    p, e = math.radians(ra), math.radians(dec)
    c = np.array([math.cos(e) * math.cos(p), math.cos(e) * math.sin(p), math.sin(e)])
    r = np.array([math.sin(p), -math.cos(p), 0.0])
    u = np.array([-math.sin(e) * math.cos(p), -math.sin(e) * math.sin(p), math.cos(e)])
    w = math.radians(roll)
    return c, math.cos(w) * r + math.sin(w) * u, -math.sin(w) * r + math.cos(w) * u


def disc_grid(n, scale):
    """Screen pixels of an n×n grid (centres, in output px) and their position on the unit disc."""
    yy, xx = (np.mgrid[0:n, 0:n] + .5) / scale
    a, b = (xx - CX) / R, (CY - yy) / R
    return a, b, np.sqrt(np.clip(1 - a * a - b * b, 0, None)), a * a + b * b <= 1


# ---------------------------------------------------------------- inputs

def tile_lut(ids):
    """(b, a) → True for DR6 tiles 'a.b' (Dec = b/2 − 90, RA = a / (2 cos Dec))."""
    lut = np.zeros((361, 721), bool)
    for t in ids:
        a, b = map(int, t.split("."))
        lut[b, a % 721] = True
    return lut


def in_tiles(lut, ra, dec):
    b = np.clip(np.round(2 * (dec + 90)).astype(int), 0, 360)
    a = np.round(2 * ra * np.cos(np.radians(b / 2 - 90))).astype(int) % 721
    return lut[b, a]


def footprint_masks(a):
    """DES, KiDS, HSC and UNIONS-3500 as HEALPix booleans at nside NS."""
    from astropy import units as u
    from mocpy import MOC
    ra, dec = hp.pix2ang(NS, np.arange(hp.nside2npix(NS)), lonlat=True)
    out = {n: MOC.from_fits(a.footprints / f"{n}.fits").contains_lonlat(ra * u.deg, dec * u.deg) for n in ("des", "kids")}
    hsc = np.load(a.footprints / "hsc_y3.npz")["mask"]           # 0.25° grid, RA 360→0, Dec −90→90
    out["hsc"] = hsc[np.round((dec + 90) / .25).astype(int), np.round((360 - ra) / .25).astype(int)]
    u35 = hp.read_map(a.u3500, dtype=np.float32)
    out["u3500"] = hp.ud_grade((u35 > 0).astype(np.float32), NS) > .5
    return out


def old_cameras(frames, masks, dr6):
    """Camera (RA, Dec, roll) of each frame of the ADE globe video, fitted to the DES envelope
    (blue or violet) and the UNIONS-3500 fill (orange) it shows."""
    from scipy.optimize import minimize
    a, b, mu, inside = disc_grid(S // 6, 1 / 6)
    keep = inside & (a * a + b * b < .94)
    a, b, mu = a[keep], b[keep], mu[keep]

    def predict(p):
        c, r, u = basis(*p)
        v = a[:, None] * r + b[:, None] * u + mu[:, None] * c
        pix = hp.vec2pix(NS, *v.T)
        return masks["des"][pix], masks["u3500"][pix]

    cams, prev = [], None
    for img in frames:
        h, s = hue_sat(img[::6, ::6][keep])
        obs_des = (s > .2) & (h > 195) & (h < 285)
        obs_u = (s > .4) & (h > 5) & (h < 35)

        def cost(p):
            d, u35 = predict(p)
            return np.mean(d != obs_des) + np.mean(u35 != obs_u)
        if prev is None:
            prev = np.array(min(((cost((p, e, 0)), (p, e, 0)) for p in range(0, 360, 6) for e in range(-80, 81, 6)))[1], float)
        res = minimize(cost, prev, method="Nelder-Mead",
                       options=dict(xatol=.05, fatol=1e-5, initial_simplex=np.vstack([prev, prev + 4 * np.eye(3)])))
        prev = res.x
        cams.append(res.x)
    return cams


def hue_sat(rgb):
    x = rgb.astype(float) / 255
    mx, mn = x.max(-1), x.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, (mx - mn) / np.maximum(mx, 1e-6)


def euclid_dr1(a, masks, dr6):
    """The Euclid DR1 footprint recovered from the ADE globe video, as a HEALPix boolean.

    Every sixth frame is fitted for its camera; its violet pixels (fill and edge, hue
    238–330°) seen at μ > 0.3 vote on a 0.1° RA–Dec grid. Cells violet in more than 40%
    of their μ²-weighted views are kept, closed over 0.5°, holes filled (the DES-blended
    fill reads blue, so the edge alone encloses it), eroded by 0.2° to take off the drawn
    edge, and patches under 1.5 deg² dropped. The result covers about 2,550 deg² against
    the MOC's 2,346 deg²; edges are good to a few tenths of a degree.
    """
    ff = imageio_ffmpeg.read_frames(str(a.old_video))
    meta = next(ff)
    frames = [np.frombuffer(f, np.uint8).reshape(meta["size"][1], meta["size"][0], 3) for k, f in enumerate(ff) if k % 6 == 0]
    cams = old_cameras(frames, masks, dr6)
    G = .1
    NX, NY = 3600, 1800
    seen, hit = np.zeros((NY, NX)), np.zeros((NY, NX))
    ga, gb, gmu, _ = disc_grid(S, 1)
    ok = gmu > .3
    ga, gb, gmu = ga[ok], gb[ok], gmu[ok]
    last = None
    for img, cam in zip(frames, cams):
        if last is not None and np.allclose(cam, last, atol=.05):
            continue
        last = cam
        c, r, u = basis(*cam)
        ra, dec = radec(ga[:, None] * r + gb[:, None] * u + gmu[:, None] * c)
        h, s = hue_sat(img[ok])
        i, j = np.clip(((dec + 90) / G).astype(int), 0, NY - 1), np.clip((ra / G).astype(int), 0, NX - 1)
        np.add.at(seen, (i, j), gmu ** 2)
        np.add.at(hit, (i, j), gmu ** 2 * ((s > .18) & (h > 238) & (h < 330)))
    m = hit > .4 * np.maximum(seen, 1e-9)
    m = ndi.binary_closing(m, np.ones((5, 5)))
    m = np.roll(ndi.binary_fill_holes(np.roll(m, NX // 2, 1)), -NX // 2, 1)
    m = ndi.binary_erosion(m, np.ones((3, 3)), iterations=2)
    lab, n = ndi.label(m)
    cell = G * G * np.cos(np.radians(np.arange(NY) * G - 90 + G / 2))[:, None] * np.ones((1, NX))
    big = np.concatenate([[False], ndi.sum(cell, lab, range(1, n + 1)) > 1.5])
    m = big[lab]
    print(f"Euclid DR1 recovered: {(m * cell).sum():,.0f} deg² in {big.sum()} patches")
    ra, dec = hp.pix2ang(NS, np.arange(hp.nside2npix(NS)), lonlat=True)
    return m[np.clip(((dec + 90) / G).astype(int), 0, NY - 1), np.clip((ra / G).astype(int), 0, NX - 1)]


def load_inputs(a):
    status = json.loads((a.footprints / "unions_dr6_status.json").read_text())
    tiles = status["tiles"]
    luts = dict(v2=tile_lut(tiles["published"]), final=tile_lut([t for g in tiles.values() for t in g]))
    cache = a.cache / "globe_masks.npz"
    if cache.exists():
        masks = {k: np.unpackbits(v)[:hp.nside2npix(NS)].astype(bool) for k, v in np.load(cache).items()}
    else:
        masks = footprint_masks(a)
        masks["dr1"] = euclid_dr1(a, masks, luts["final"])
        a.cache.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache, **{k: np.packbits(v) for k, v in masks.items()})
    area = hp.nside2pixarea(NS, degrees=True)
    print("  ".join(f"{k} {v.sum() * area:,.0f} deg²" for k, v in masks.items()))
    return masks, luts


def load_gaia(path):
    Image.MAX_IMAGE_PIXELS = None
    tex = np.asarray(Image.open(path).convert("RGB").resize((2400, 1200), Image.LANCZOS), np.float32)
    grey = tex.mean(-1, keepdims=True)
    return (grey + .55 * (tex - grey)) * .62


# ---------------------------------------------------------------- frames

G = {}


def init(state):
    G.update(state)
    a, b, mu, inside = disc_grid(S * SS, SS)
    G["grid"] = a[inside], b[inside], mu[inside]
    G["inside"] = inside
    G["edge_alpha"] = ndi.uniform_filter(inside.astype(np.float32), SS)[SS // 2::SS, SS // 2::SS]
    G["font"] = ImageFont.truetype(str(G["font_path"]), 46, index=1)


def gaia(v):
    g = v @ EQ2GAL.T
    l = np.degrees(np.arctan2(g[:, 1], g[:, 0]))
    b = np.degrees(np.arcsin(np.clip(g[:, 2], -1, 1)))
    tex = G["gaia"]
    th, tw = tex.shape[:2]
    x = (((.5 - l / 360) % 1) * tw).astype(int) % tw
    y = np.clip(((90 - b) / 180 * th).astype(int), 0, th - 1)
    return tex[y, x] + np.float32(24)


def edge(mask, width):
    """A line `width` supersampled px wide along the boundary of a supersampled boolean image."""
    return ndi.maximum_filter(mask, width) & ~ndi.minimum_filter(mask, width)


def down(x):
    n = S * SS
    return x.reshape(S, SS, S, SS, *x.shape[2:]).mean((1, 3)) if x.shape[0] == n else x


def render(job):
    i, view = job
    c, r, u = basis(*view)
    a, b, mu = G["grid"]
    v = a[:, None] * r + b[:, None] * u + mu[:, None] * c
    ra, dec = radec(v)
    pix = hp.vec2pix(NS, *v.T)
    m = G["masks"]
    layers = [(m["des"][pix], DES), (m["kids"][pix], KIDS), (m["hsc"][pix], HSC),
              (in_tiles(G["luts"]["v2"], ra, dec), V2), (m["u3500"][pix], U3500), (m["dr1"][pix], DR1)]
    final = in_tiles(G["luts"]["final"], ra, dec)

    col = gaia(v)
    n = S * SS
    inside = G["inside"]

    def full(x):
        out = np.zeros((n, n) + x.shape[1:], x.dtype)
        out[inside] = x
        return out
    img = full(col)
    shade = full((.78 + .22 * mu).astype(np.float32))
    # graticule: Dec every 30°, RA every 30°, antialiased by the screen gradient
    for f in (full(dec / 30), full(ra / 30)):
        gy, gx = np.gradient(f)
        g = np.hypot(gx, gy)
        g[g > .2] = np.inf      # the RA seam and the poles
        d = np.abs(f - np.round(f)) / np.maximum(g, 1e-9)
        line = np.clip(1.6 - d / SS, 0, 1) * inside * .32
        img = img * (1 - line[..., None]) + 205 * line[..., None]
    for mask, (rgb, alpha) in layers:
        mk = ndi.binary_closing(full(mask), np.ones((9 * SS, 9 * SS)))   # star-mask pinholes and tile seams
        img = np.where(mk[..., None], img * (1 - alpha) + np.array(rgb, np.float32) * alpha, img)
        e = edge(mk, 3 * SS) & inside
        img[e] = rgb
    img[edge(ndi.binary_closing(full(final), np.ones((9 * SS, 9 * SS))), 4 * SS) & inside] = FINAL
    img *= shade[..., None]
    img = down(img)
    w = G["edge_alpha"][..., None]
    img = img * w + np.array(GROUND, np.float32) * (1 - w)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

    d = ImageDraw.Draw(im)
    for text, lra, ldec, colour in LABELS:
        p = unit(lra, ldec)
        k = float(np.clip((p @ c - .25) / .2, 0, 1))
        if k == 0:
            continue
        x, y = CX + R * (p @ r), CY - R * (p @ u)
        over = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(over).text((x, y), text, font=G["font"], anchor="mm", fill=colour + (int(255 * k),),
                                  stroke_width=5, stroke_fill=(18, 16, 22, int(235 * k)))
        im.paste(over, (0, 0), over)
    return i, im.tobytes()


def ease(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def path():
    """(RA, Dec) of the globe centre in every frame."""
    views = []
    n = [round(t * FPS) for t in (T_SOUTH, T_TRAVEL, T_PRECESS, T_HOLD)]
    for k in range(n[0]):
        views.append(SOUTH)
    for k in range(n[1]):
        s = ease((k + 1) / n[1])
        views.append((SOUTH[0] + (HOLD[0] - SOUTH[0]) * s, SOUTH[1] + (HOLD[1] - SOUTH[1]) * s))
    for k in range(n[2]):
        s = (k + 1) / n[2]
        env = ease(s / .18) * ease((1 - s) / .18)          # the cone opens and closes smoothly
        th = 2 * math.pi * s                                # south, east, north, west edges in turn
        dec = HOLD[1] - CONE * env * math.cos(th)
        views.append((HOLD[0] + CONE * env * math.sin(th) / math.cos(math.radians(dec)), dec))
    views += [HOLD] * n[3]
    return views


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--footprints", type=Path, default=HOME / "scratch/talk-ade/talk-ade-2026/figures/data/footprints")
    ap.add_argument("--u3500", type=Path, default=HOME / "Downloads/mask_map_footprint_nside_4096.fits")
    ap.add_argument("--gaia", type=Path, default=HOME / "Downloads/unions-eiffel-composites/assets/gaia_edr3_colour_equirectangular.png")
    ap.add_argument("--old-video", type=Path, default=HOME / "Documents/projects/talk-ade-2026/media/globe_surveys.mp4")
    ap.add_argument("--cache", type=Path, default=HOME / "scratch/globe/cache")
    ap.add_argument("--font", type=Path, default=Path("/System/Library/Fonts/Helvetica.ttc"), help="Helvetica .ttc (bold is face 1)")
    ap.add_argument("--jobs", type=int, default=max(1, mp.cpu_count() - 2))
    ap.add_argument("--frames", default="", help="comma-separated frame indices to write as PNGs")
    a = ap.parse_args()

    masks, luts = load_inputs(a)
    state = dict(masks=masks, luts=luts, gaia=load_gaia(a.gaia), font_path=a.font)
    views = path()
    jobs = list(enumerate(views))
    print(f"{len(jobs)} frames, {len(jobs) / FPS:.1f} s")
    with mp.get_context("fork").Pool(a.jobs, initializer=init, initargs=(state,)) as pool:
        if a.frames:
            for i, raw in pool.imap(render, [jobs[int(k)] for k in a.frames.split(",")]):
                Image.frombytes("RGB", (S, S), raw).save(a.cache / f"globe_{i:04d}.png")
            return
        out = IMAGES / "unions_globe_surveys.mp4"
        ff = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{S}x{S}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                               "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
        for i, raw in pool.imap(render, jobs, chunksize=2):
            ff.stdin.write(raw)
            last = raw
        ff.stdin.close()
        assert ff.wait() == 0
        Image.frombytes("RGB", (S, S), last).save(out.with_suffix(".jpg"), quality=92)
        print("→", out, out.with_suffix(".jpg"))


if __name__ == "__main__":
    main()
