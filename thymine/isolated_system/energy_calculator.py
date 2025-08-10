import numpy as np
import os 

from wrappers.orca_wrappers import sf_orca_run
from ase.io import read

"""
TDDFT Excited State Energy Calculations

Energy calculations on the isolated relaxed geometries calculated in `geometry_optimiser.ipynb`.
"""

energy_path = 'thymine/isolated_system/energies'
geom_path = 'thymine/isolated_system/geometry_optimisations'
number_excited_states = 2
orca_task = 'Engrad'
orca_basis_set = 'wB97M-D3BJ'
orca_func = 'def2-TZVPPD'

geometries = os.listdir(geom_path)

# Spin-Flip Linear Response


for i in range(1, number_excited_states + 1):
    for geometry in geometries:
        angle = geometry.split('_')[-1]
        orca_block = f'%pal nprocs 16 end \n%tddft nroots {number_excited_states} Iroot {i}\n sf true \nend'

        calculation_dir = f'{energy_path}/state_{i}_angle_{angle}'
        if os.path.exists(os.path.join(calculation_dir, 'orca.out')):
            print(f'Orca SF-TDDFT Calculation Found for, Angle {angle}')
        else:
            molecule = read(f'{geom_path}/{geometry}/orca.xyz')
            calculation_dir = f'{energy_path}/state_{i}_angle_{angle}'
            sf_orca_run(molecule, calculation_dir, orca_task, orca_basis_set, orca_func, orca_block)
            print(f'Orca SF-TDDFT Calculation Finished on Angle {angle}')