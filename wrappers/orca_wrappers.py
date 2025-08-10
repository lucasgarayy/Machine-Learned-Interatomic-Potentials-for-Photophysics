from os import environ, path, makedirs, chdir, getcwd, remove, symlink
from ase.io import read
# Set up a record of the original working directory in case we get lost by interrupting calculations
if 'assignment_dir' not in locals():
    assignment_dir = getcwd()
chdir(assignment_dir)

# Number of processors to use
nprocs = 8

# Set up ORCA
from ase.calculators.orca import ORCA, OrcaProfile
orca_cmd = "/software/easybuild/software/ORCA/6.0.0-gompi-2023b/bin/orca"
orca_profile = OrcaProfile(command=orca_cmd)
orca_pal_block = '%pal nprocs 8 end'

import tempfile

# Wrapper for running neat-and-tidy ORCA calculations that clean up
# after themselves and only write to local scratch space while running.
# It assumes we start from a working directory on the home or storage drives.
# It makes a directory for the calculation result, then creates a temporary
# directory under /tmp on the local filesystem. It switches to that directory,
# makes links so the calculation's text outputs will be written back to the
# original directory, creates a calculator based on the input variables, then
# runs the calculation. After returning to the original directory, the temporary
# folder is destroyed.

# The arguments to this routine are:
#    model (ASE Atoms object): the model to perform the calculation on
#    directory (string): directory to run the calculation in and hold all results)
#    task (string): what task ORCA is to perform, eg EnGrad or Opt
#    basis_set (string): the name of the basis set, eg "def2-SVP"
#    func (string): the name of the XC functional, eg "PBE"
# Parallelism blocks and orca profiles are defined in the box at the top
def orca_run(model,directory,task,basis_set,func, mult, orca_blocks=""):
    from ase.optimize import BFGS
    origdir = getcwd()
    if not path.exists(directory):
        makedirs(directory) # make copy in original working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f'Calculation executing in {tmpdir}')
        chdir(tmpdir) # move to temporary directory
        makedirs(directory) # make directory within temporary directory for calculation
        # make symlinks so text-only output files files write to original directory
        for ext in ['.out','.err','.inp','.xyz','_trj.xyz','.engrad','_property.txt']:
            symlink(f'{origdir}/{directory}/orca{ext}',f'{tmpdir}/{directory}/orca{ext}')
        model.calc = ORCA(directory=directory,
                          orcasimpleinput=f"{task} {basis_set} {func}",
                          profile=orca_profile,orcablocks=orca_pal_block+orca_blocks, mult = mult)
        model.get_potential_energy()
        chdir(origdir) # return to original directory, large output files are discarded
    return # do not return any values - use orca_load


# Same function as orca_run but to run calculations using Spin-Flip
def sf_orca_run(model,directory,task,basis_set,func,orca_blocks=""):
    from ase.optimize import BFGS
    origdir = getcwd()
    if not path.exists(directory):
        makedirs(directory)
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f'Calculation executing in {tmpdir}')
        chdir(tmpdir) 
        makedirs(directory)

        for ext in ['.out','.err','.inp','.xyz','_trj.xyz','.engrad','_property.txt']:
            symlink(f'{origdir}/{directory}/orca{ext}',f'{tmpdir}/{directory}/orca{ext}')
        model.calc = ORCA(directory=directory,
                          orcasimpleinput=f"{task} {basis_set} {func}",
                          profile=orca_profile,orcablocks=orca_pal_block+orca_blocks, mult=3)
        model.get_potential_energy()
        chdir(origdir) 
    return 

# Wrapper to load the result of a previously-completed ORCA calculation.
# Unfortunately loading the results of a completed ORCA singlepoint or
# geometry optimisation calculation cannot be achieved in
# a single step: we need to read the coordinates first, then read
# the energy and forces and attach the results as a SinglePointCalculator
# I have put this into a straightforward routine below.
def orca_load(directory):
    from ase.io.orca import read_orca_outputs, read_geom_orcainp
    from ase.calculators.singlepoint import SinglePointCalculator
    xyz_file = f"{directory}/orca.xyz"
    input_file = f"{directory}/orca.inp"
    output_file = f"{directory}/orca.out"
    if path.exists(xyz_file):
        atoms = read(xyz_file)
    else:
        atoms = read_geom_orcainp(input_file)
    atoms.calc = SinglePointCalculator(atoms)
    atoms.calc.results = read_orca_outputs(directory,output_file)
    return atoms
