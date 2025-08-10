import numpy as np
from ase.io import read
from wrappers.orca_wrappers import orca_run
import os





task = 'opt'
basis = 'def2-TZVPPD'
func = 'wB97M-D3BJ'
out_dir = 'thymine/isolated_system/geometry_optimisations'
molecule = read('thymine/isolated_system/di-thymine.xyz') # Basic Di-Thymine structure file
c5_c5prime = np.linspace(2.6, 3.6, 6)
c5_c5_c6 = np.linspace(34, 98, 8)


for length in c5_c5prime:
    for angle in c5_c5_c6:
        calc_dir = f'{out_dir}/length_{length:.2f}_angle_{angle:.2f}'
        if os.path.exists(os.path.join(calc_dir, 'orca.out')):
            print(f'Orca Geometry Calculation Found for Length: {length}, Angle: {angle}')
            continue
        print(f'Starting on Length: {length}, angle: {angle}')
        orca_block = f'%geom Constraints \n{{B 9 8 {length} C}} \n{{A 8 9 11 {angle} C}} \n end \n end'
        orca_run(molecule, calc_dir , task, basis, func, orca_block)
        print(f'Orca Geometry Calculation Finished on Length: {length}, angle: {angle}')