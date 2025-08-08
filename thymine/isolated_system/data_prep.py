import os
import sys

from ase.io import read, write
from wrappers.orca_wrappers import orca_load
from pathlib import Path
from ase import Atoms
from wrappers.orca_wrappers import orca_load ,orca_run

input_dir = 'thymine/isolated_system/energies'

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



out_dir = 'mace-suite/data/unprocessed_datasets/thymine'
os.makedirs(out_dir, exist_ok=True)
write(f'{out_dir}/thymine_lr-gs.xyz', lr_gs)
write(f'{out_dir}/thymine_lr-es1.xyz', lr_es1)
write(f'{out_dir}/thymine_sf-es1.xyz', sf_es1)
write(f'{out_dir}/thymine_sf-es2.xyz', sf_es2)

example = lr_gs[0]
atom_species = example.get_chemical_symbols().keys()

e0s = []

orca_task = 'SP'
orca_func = 'wB97M-D3BJ'
orca_basis = 'def2-TZVPPD'
e0s_dir = 'thymine/isolated_system/single_point_energies'

for atom in atom_species:
    calc_dir = f'{e0s_dir}/{atom}'
    if os.path.exists(calc_dir):
        print(f'SPE Calculation already performed for atom: {atom}')
    else:
        ase_atom = Atoms([atom])
        if atom == 'H' or atom == 'N':
            orca_run(ase_atom, calc_dir, orca_task, orca_func, orca_basis, mult= 2)
        else:
            orca_run(ase_atom, calc_dir, orca_task, orca_func, orca_basis, mult= 1)
        print(f"Performing SPE Calculation for atom: {atom}")

    calc_result = orca_load(calc_dir)
    e0s.append(calc_result)

write(f"{out_dir}/E0s.xyz", e0s)