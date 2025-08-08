import numpy as np
import os 

from wrappers.orca_wrappers import orca_run
from ase.data.pubchem import pubchem_atoms_search


"""
Geometry Optimisation

Runs geometry optimisations subject to the angle constraint mentioned in the paper
"""

orca_path = 'oxirane/isolated_system/geometry_optimisations'
orca_task = 'Opt'
orca_basis_set = 'wB97M-D3BJ'
orca_func = 'def2-TZVPPD'

molecule_name = 'oxirane'
molecule_angles = [2, 1, 0]

angle_range = np.linspace(60, 150, 60)
molecule = pubchem_atoms_search(name=molecule_name)


for angle in angle_range:
    constraint_block = f'\n%geom\nConstraints\n    {{A 2 1 0 {angle} C }}\nend\nMaxIter 200\nend'
    orca_block = f' %pal nprocs 64 end {constraint_block}'
    calculation_dir = f'{orca_path}/angle_{angle:.2f}'
    if os.path.exists(os.path.join(calculation_dir, 'orca.out')):
        print(f'Orca Geometry Calculation Found for, Angle {angle}')
    else:
        molecule.set_angle(*molecule_angles, angle, add=False)
        calculation_dir = f'{orca_path}/angle_{angle}'
        orca_run(molecule, calculation_dir, orca_task, orca_basis_set, orca_func, orca_block)
        print(f'Orca Geometry Calculation Finished on Angle {angle}')