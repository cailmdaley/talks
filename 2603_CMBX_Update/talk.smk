"""Snakemake rules for 2603_CMBX_Update talk figures."""

TALK_DIR = Path("docs/talks/2603_CMBX_Update")
TALK_IMAGES = TALK_DIR / "images"

localrules: talk_footprint_south, talk_xl_galactic_extinction


rule talk_footprint_south:
    """South-patch-only footprint overlap for slide 3."""
    input:
        act_mask=data_dir / cmb_experiments["act"]["mask"],
        spt_mask=data_dir / cmb_experiments["spt_winter_gmv"]["mask"],
        shear_pkl=Path("/leonardo_work/EUHPC_E05_083/cmbx/outputs/maps/test_maps_refactor/rr2_v2_1_031224/maps_wl_lensmc_nside-2048.pkl"),
    output:
        png=TALK_IMAGES / "footprint_south.png",
    log:
        "workflow/logs/talk_footprint_south.log",
    params:
        all_bin_idx=_bin_to_idx("all"),
    resources:
        mem_mb=16000,
    script:
        "scripts/plot_footprint_south.py"


rule talk_xl_galactic_extinction:
    """Galactic extinction X_l composite: density + lensmc × ACT / SPT GMV / SPT PP."""
    input:
        cmbk_sys_npz=expand(
            tapestry_dir / "compute_cmbk_systematic_cross_spectrum"
            / "galactic_extinction_x_{cmbk}_cls.npz",
            cmbk=["act", "spt_winter_gmv", "spt_winter_pp"],
        ),
        sys_npz=expand(
            tapestry_dir / "compute_systematic_cross_spectrum"
            / "galactic_extinction_x_{method}_bin{bin}_cls.npz",
            method=["lensmc", "density"],
            bin=tom_bins,
        ),
        signal_ref=expand(
            out_dir / "spectra" / "{method}_bin3_x_{cmbk}_cls.npz",
            method=["lensmc", "density"],
            cmbk=["act", "spt_winter_gmv", "spt_winter_pp"],
        ),
    output:
        png=TALK_IMAGES / "xl_galactic_extinction.png",
    script:
        "scripts/plot_xl_galactic_extinction.py"
