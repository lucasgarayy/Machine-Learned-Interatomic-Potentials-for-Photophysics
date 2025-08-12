import os
import sys

from ase.io import read, write
from pathlib import Path
from ase import Atoms
from wrappers.orca_wrappers import orca_load ,orca_run

input_dir = 'oxirane/molecular_dynamics/snapshots_energies'

sf_es1 = []
sf_es2 = []

targets = {
    1: sf_es1,  # SF ES1
    2: sf_es2,  # SF ES2
}

for state_folder in Path(input_dir).iterdir():
    if not state_folder.is_dir():
        continue
    try:
        state_idx = int(state_folder.name.split('_')[1])
    except (IndexError, ValueError):
        continue

    bucket = targets.get(state_idx)
    if bucket is None:
        continue

    for run_folder in state_folder.iterdir():
        if run_folder.is_dir():
            bucket.append(orca_load(run_folder))

out_dir = 'mace-suite/data/unprocessed_datasets/oxirane/molecular_dynamics'
os.makedirs(out_dir, exist_ok=True)

write(f'{out_dir}/oxirane_md-es1.xyz', sf_es1)
write(f'{out_dir}/oxirane_md-es2.xyz', sf_es2)

if sf_es1:
    example = sf_es1[0]
elif sf_es2:
    example = sf_es2[0]
else:
    raise RuntimeError("No SF data found in 'oxirane/molecular_dynamics/snapshots_energies'.")

atom_species = set(example.get_chemical_symbols())

e0s = []

orca_task = 'SP'
orca_func = 'wB97M-D3BJ'
orca_basis = 'def2-TZVPPD'
e0s_dir = 'oxirane/isolated_system/single_point_energies'

for atom in atom_species:
    calc_dir = f'{e0s_dir}/{atom}'
    if os.path.exists(calc_dir):
        print(f'SPE Calculation already performed for atom: {atom}')
    else:
        ase_atom = Atoms([atom])
        if atom in ('H', 'N'):
            orca_run(ase_atom, calc_dir, orca_task, orca_func, orca_basis, mult=2)
        else:
            orca_run(ase_atom, calc_dir, orca_task, orca_func, orca_basis, mult=1)
        print(f"Performing SPE Calculation for atom: {atom}")

    calc_result = orca_load(calc_dir)
    calc_result.info['config_type'] = 'IsolatedAtom'
    calc_result.info['REF_energy'] = calc_result.get_potential_energy()
    e0s.append(calc_result)

write(f"{out_dir}/E0s.xyz", e0s)
