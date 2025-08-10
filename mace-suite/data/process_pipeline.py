import os
from ase.io import read, write
import random
import pandas as pd



def combine_split_xyz_files(input_file_dirs, output_folder, train_ratio=0.8, duplicate_data=False, filter_sf=True, return_combined = False):
    samples_by_head_type = {}
    e0s = []
    samples_dict = {}
    for file in os.listdir(input_file_dirs):
        if file == 'E0s.xyz':
            e0s_file = read(f'{input_file_dirs}/{file}', index=":")
            samples_dict['E0s'] = len(e0s_file)
            e0s.extend(e0s_file)

        if file.endswith('.xyz') and ('sf' in file if filter_sf else True):
            head_type = file.split('_')[-1]
            sample_type = file.split('_')[0]
            
            if head_type not in samples_by_head_type:
                samples_by_head_type[head_type] = {}
            if sample_type not in samples_by_head_type[head_type]:
                samples_by_head_type[head_type][sample_type] = []
            
            file_path = f'{input_file_dirs}/{file}'
            frames = read(file_path, index=":")
            
            molecules_by_type = []
            for t in frames:
                tp = t.copy()
                tp.info["REF_energy"] = t.calc.results["energy"]
                tp.arrays["REF_forces"] = t.calc.results["forces"]
                molecules_by_type.append(tp)
            
            samples_by_head_type[head_type][sample_type] += molecules_by_type
            samples_dict[sample_type] = len(frames)
    
    for head_type in samples_by_head_type:
        for sample_type in samples_by_head_type[head_type]:
            random.shuffle(samples_by_head_type[head_type][sample_type])
    
    if duplicate_data:
        for head_type in samples_by_head_type:
            for sample_type in samples_by_head_type[head_type]:
                samples_by_head_type[head_type][sample_type] *= 2
        for sample in samples_dict.keys():
            if sample != 'E0s':
                samples_dict[sample] *= 2
    

    for head in samples_by_head_type.keys():
        combined_data = []
        for sample_type in samples_by_head_type[head]:
            combined_data.extend(samples_by_head_type[head][sample_type])

            molecules = samples_by_head_type[head][sample_type]
            num_molecules = len(molecules)
            num_train = int(train_ratio * num_molecules)
            train_molecules = molecules[:num_train] + e0s
            val_molecules = molecules[num_train:] + e0s
            write(f'{output_folder}/train_{sample_type}_{head[:-4]}.xyz', train_molecules)
            write(f'{output_folder}/validation_{sample_type}_{head[:-4]}.xyz', val_molecules)

        if return_combined:
            num_molecules = len(combined_data)
            num_train = int(train_ratio * num_molecules)

            combined_train = combined_data[:num_train] + e0s
            combined_validation = combined_data[num_train:] + e0s

        
            write(f'{output_folder}/train_combined_{head[:-4]}.xyz', combined_train)
            write(f'{output_folder}/validation_combined_{head[:-4]}.xyz', combined_validation)
    
    df = pd.DataFrame(samples_dict.items(), columns=['Sample', 'Number of molecules'])
    df.to_csv(f'{output_folder}/samples_info.csv', index=False)

output_folder = 'mace-suite/data/processed_datasets'
input_folder = 'mace-suite/data/unprocessed_datasets'

systems = os.listdir(input_folder)

"""
Process dataset by type, 2 separate datasets:
    - Isolated 
    - MD 

MD data will not be ready until first model is trained with Isolated dataset as mentioned in the README.
        
"""
for system in systems:
    system_data_types = os.listdir(f'{input_folder}/{system}') 

    system_output_folder = f'{output_folder}/{system}'
    os.makedirs(system_output_folder, exist_ok= True)

    for system_data_type in system_data_types:

        system_data_input_folder = f'{input_folder}/{system}/{system_data_type}'
        system_data_output_folder = f'{output_folder}/{system}/{system_data_type}'
        os.makedirs(system_data_output_folder, exist_ok=True)
        combine_split_xyz_files(system_data_input_folder, system_data_output_folder, duplicate_data= True, filter_sf= True, return_combined= False)
    
