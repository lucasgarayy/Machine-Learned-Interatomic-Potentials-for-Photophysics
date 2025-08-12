import numpy as np 
from ase.units import fs
from ase.md.langevin import Langevin
from ase.md import MDLogger
from ase.io import read, write
from mace.calculators import MACECalculator
from wrappers.orca_wrappers import sf_orca_run
import torch

import os

class XYZLogger(MDLogger):
    def __init__(self, dyn, atoms, snapshot_dir, **kwargs):

        super().__init__(dyn, atoms, snapshot_dir, **kwargs)
        self.snapshot_dir = snapshot_dir
        self.atoms = atoms

    def log_snapshot(self):
        step = self.dyn.nsteps
        new_snapshot_dir = f"{self.snapshot_dir}_step_{step}"
        os.makedirs(new_snapshot_dir, exist_ok=True)
        xyz_filename = f"{new_snapshot_dir}/snapshot.xyz"
        write(xyz_filename, self.atoms)

        print(f"Snapshot saved: {xyz_filename}")
    
    def __call__(self):
        self.log_snapshot()

isolated_model_path = "thymine/molecular_dynamics/isolated_model/thymine_isolated_compiled.model"
device = 'cuda' if torch.cuda.is_available() else 'cpu'
calculator = MACECalculator(model_paths = isolated_model_path, device = device)

sampled_lengths = [2.6, 3.0, 3.2, 3.4, 3.6]
sampled_angles = [34.0, 52.29, 70.57, 79.71, 98.0]
snapshots = 500
log_steps = [5, 10, 50, 200, 500]


def custom_logging():
    if dyn.nsteps in log_steps:
        logger()
        print(f"Logged step {dyn.nsteps}")


for length in sampled_lengths:
    for angle in sampled_angles:        

        atoms_path = f"thymine/isolated_system/geometry_optimisations/length_{length}_angle_{angle}/orca.xyz"
        atoms = read(atoms_path)
        atoms.calc = calculator
        dyn = Langevin(atoms, timestep = 0.5 *fs, temperature_K = 300, friction = 0.01/fs)
        logfile = f"thymine/molecular_dynamics/logs/length_{length}_angle_{angle}"
        snapshot_dir = f"thymine/molecular_dynamics/snapshots/length_{length}_angle_{angle}"
        os.makedirs(logfile, exist_ok=True)
        logger = XYZLogger(dyn, atoms, snapshot_dir)
        energy_logger = MDLogger(dyn, atoms, f"{logfile}/logger.log")
        dyn.attach(custom_logging, interval=1)
        dyn.attach(energy_logger)
        dyn.run(500)


xyz_dir = 'thymine/molecular_dynamics/snapshots'
snapshots_dir = os.listdir(xyz_dir)

task = 'Engrad'
basis = 'def2-TZVPPD'
func = 'wB97M-D3BJ'
num_states = 2
for state in range(1, num_states + 1):
    for snapshot in snapshots_dir:
        calc_dir = f'thymine/molecular_dynamics/snapshots_energies/sf-es_{state}/{snapshot}'
        if os.path.exists(f'{calc_dir}/orca.out'):
            print("Calculation found")
            continue
        try:
            atoms = read(f'{xyz_dir}/{snapshot}/snapshot.xyz')
            orca_block = f'%pal nprocs 32 end \n%tddft Nroots 2 Iroot {state} \nsf true \nend'
            sf_orca_run(atoms, calc_dir, task, basis, func, orca_block)
        except:
            pass

        