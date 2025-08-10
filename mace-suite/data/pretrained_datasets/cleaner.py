import os
from ase.io import read, write
import re
import random

class ptDataCleaner:
    def __init__(self, in_str, out_str, elements, n_samples):
        self.str = in_str
        self.out_str = out_str
        self.parsed_atoms = self.parse_ref(self.str, self.str)
        self.elements = elements
        self.n_samples = n_samples
        self.good_mols = self.filter_atoms()

    def parse_ref(self, path, output_path):
        with open(path, 'r') as file:
            lines = file.readlines()
        new_lines = []

        for line in lines:
            if "energy" in line:
                line = line.replace(" energy", " REF_energy")
            if ":forces" in line:
                line = line.replace(":forces", ":REF_forces")
            new_lines.append(line)

        with open(output_path, 'w') as file:
            file.writelines(new_lines)

        return(read(output_path, index = ':'))

    def filter_atoms(self):
        good_mols = []
        for molecule in self.parsed_atoms:
            unique_elements = list(dict.fromkeys(re.findall(r'[A-Z][a-z]?', str(molecule.symbols))))
            if all (ele in self.elements for ele in unique_elements):
                good_mols.append(molecule)
        return good_mols    
    
    def random_sample(self):
        random_selection = random.sample(self.good_mols, self.n_samples)
        return write(self.out_str, random_selection)
    

input_file = 'mace-suite/data/pretrained_datasets/test_large_neut_all.xyz'
output_file = 'mace-suite/data/pretrained_datasets/cleaned/cleaned_pt_train.xyz'
elements = ['C', 'O', 'N', 'H']

cleaner = ptDataCleaner(input_file, output_file, elements=elements, n_samples=500)
cleaner.random_sample()