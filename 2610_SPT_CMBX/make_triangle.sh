#!/bin/bash
# The systematics-triangle slide on Cycle 2: TR1 v2 official-bin template crosses
# (root results/tr1_v2/systematics) in units of sigma_G from the Cycle-2 SPT
# likelihood_input given as $1. make_systematics.py asserts that its field windows
# hash to the null family's, so a likelihood_input from other catalogues fails.
#   bash 2610_SPT_CMBX/make_triangle.sh <path>/results/tr1_v2/likelihood_product/likelihood_input.tar
# then rebuild the deck and run private/snapshot_systematics.cjs with prefix systematics_spt.
set -euo pipefail
source ~/loom/shell-functions.sh   # app: the cmbx container
cd "$(dirname "$0")/private"
app python make_systematics.py --cycle2 --only-cycle2 --likelihood-input "$1" --output systematics_spt.json
app python render_systematics.py --even-bars --source systematics_spt.json --prefix systematics_spt
