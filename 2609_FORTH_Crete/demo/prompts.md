# FORTH live tutorial — prompts (paste into the agent, in order)

## 1

Download the Union2.1 supernova compilation from the Supernova Cosmology Project into a data/
directory:

https://supernova.lbl.gov/Union/figures/SCPUnion2.1_mu_vs_z.txt

Then show me the first few rows and tell me what's in the file.

## 2

Use the astra skill to set up an astra.yaml for this. I want to fit a flat LCDM model to this
data to recover Omega_Lambda, varying only Omega_Lambda and using the metadata in the file's
header.

Two outputs: the best fit, and a downstream best-fit Hubble diagram figure with an absolute panel
and a residuals panel. Put outputs under results/, e.g. results/hubble_diagram.png.

In this first pass, let's only use inputs, outputs, and recipes. Please walk me through each
element that you add.

## 3

Use uv to set up a virtual environment and install any needed packages.

Then implement the analysis. Write the scripts the recipes call, run them, and show me the Hubble
diagram. Save the figure to results/hubble_diagram.png.

## 4

The paper that published this catalogue is Suzuki et al. 2012, arXiv 1105.3470. Cache the paper,
verify their own Omega_Lambda from these supernovae, and show me the output. Then record it in
astra.yaml as a prior insight with the quote as evidence, and tell me how our constraint compares
to theirs.

## 5

Let's understand why our error bars are so much tighter than theirs. Download the two Union2.1
covariance files:

https://supernova.lbl.gov/Union/figures/SCPUnion2.1_covmat_nosys.txt
https://supernova.lbl.gov/Union/figures/SCPUnion2.1_covmat_sys.txt

Work out which one the main data file's error column is using, then add a decision to astra.yaml
to switch to the other, and see what impact it has on our constraint.
