import os
import sys

from ase.io import read, write
from wrappers.orca_wrappers import orca_load
from pathlib import Path


input_dir = 'isolated_systems/oxirane/energies'

lr_gs = []
lr_es1 = []
sf_es1 = []
sf_es2 = []
targets = {
    ('lr', 0): lr_gs,
    ('lr', 1): lr_es1,
    ('sf', 1): sf_es1,
    ('sf', 2): sf_es2,
}

for (subfolder, state_idx), bucket in targets.items():
    for run in (Path(input_dir) / subfolder).iterdir():
        if int(run.name.split('_')[1]) == state_idx:
            bucket.append(orca_load(run))



out_dir = 'mace-suite\ç/data/unprocessed_datasets/oxirane'
os.makedirs(out_dir, exist_ok=True)
write(f'{out_dir}/oxirane_lr-gs.xyz', lr_gs)
write(f'{out_dir}/oxirane_lr-es1.xyz', lr_es1)
write(f'{out_dir}/oxirane_sf-es1.xyz', sf_es1)
write(f'{out_dir}/oxirane_sf-es2.xyz', sf_es2)