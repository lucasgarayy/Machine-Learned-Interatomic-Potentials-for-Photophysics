import numpy as np
import os 

from wrappers.orca_wrappers import sf_orca_run, orca_run, orca_load
from ase.io import read

"""
TDDFT Excited State Energy Calculations

Energy calculations on the isolated relaxed geometries calculated in `geometry_optimiser.ipynb`.
2 Sets of calculations:
    - Conventional Linear Response
    - Spin-Flip Linear Response
"""

lr_energy_path = 'isolated_systems/oxirane/energies/linear-response'
sf_energy_path = 'isolated_systems/oxirane/energies/spin-flip'
geom_path = 'isolated_systems/oxirane/geometry_optimisations'
number_excited_states = 2
orca_task = 'Engrad'
orca_basis_set = 'wB97M-D3BJ'
orca_func = 'def2-TZVPPD'

molecule_name = 'oxirane'

geometries = os.listdir(geom_path)

# Convetional Linear Response

for i in range(0, number_excited_states):
    for geometry in geometries:
        angle = geometry.split('_')[-1]
        orca_block = f'%pal nprocs 16 end \n%tddft nroots {number_excited_states} Iroot {i}\n sf true \nend'
        calculation_dir = f'{lr_energy_path}/state_{i}_angle_{angle}'
        if os.path.exists(os.path.join(calculation_dir, 'orca.out')):
            print(f'Orca LR-TDDFT Calculation Found for, Angle {angle}')
        else:
            molecule = read(f'{geom_path}/{geometry}/orca.xyz')
            calculation_dir = f'{lr_energy_path}/state_{i}_angle_{angle}'
            orca_run(molecule, calculation_dir, orca_task, orca_basis_set, orca_func, orca_block)
            print(f'Orca LR-TDDFT Calculation Finished on Angle {angle}')


# Spin-Flip Linear Response


for i in range(1, number_excited_states + 1):
    for geometry in geometries:
        angle = geometry.split('_')[-1]
        orca_block = f'%pal nprocs 16 end \n%tddft nroots {number_excited_states} Iroot {i}\n sf true \nend'

        calculation_dir = f'{sf_energy_path}/state_{i}_angle_{angle}'
        if os.path.exists(os.path.join(calculation_dir, 'orca.out')):
            print(f'Orca SF-TDDFT Calculation Found for, Angle {angle}')
        else:
            molecule = read(f'{geom_path}/{geometry}/orca.xyz')
            calculation_dir = f'{sf_energy_path}/state_{i}_angle_{angle}'
            sf_orca_run(molecule, calculation_dir, orca_task, orca_basis_set, orca_func, orca_block)
            print(f'Orca SF-TDDFT Calculation Finished on Angle {angle}')