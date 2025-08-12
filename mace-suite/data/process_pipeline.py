import os
from ase.io import read, write
import random
import pandas as pd
import re


import os
import re
import random
import pandas as pd
from ase.io import read, write

def combine_split_xyz_files(
    input_file_dir,
    output_folder,
    train_ratio=0.8,
    duplicate_data=False,
    filter_sf=True,
    combined=False,
):
    """
    Reads .xyz files in `input_file_dir`, groups them by the '-esX' suffix found at
    the end of the filename (before .xyz), and writes train/validation splits to `output_folder`.

    Behavior:
      - If `combined` is False: keeps *original naming* from head type in input files.
      - If `combined` is True: for each esX, combine all sample_types into a single dataset,
        and write train_{esX}.xyz / validation_{esX}.xyz.

    Notes:
      - E0s.xyz is appended to both train and validation if present.
      - If `filter_sf` is True, only files containing 'es' are considered.
    """

    os.makedirs(output_folder, exist_ok=True)

    samples_dict = {}
    e0s = []
    e0s_path = os.path.join(input_file_dir, 'E0s.xyz')
    if os.path.isfile(e0s_path):
        e0s = list(read(e0s_path, index=":"))
        samples_dict['E0s'] = len(e0s)

    datasets = {}  # datasets[es_key][(sample_type, head)] = [frames]

    def extract_es_key(filename_tail: str) -> str | None:
        base = filename_tail[:-4]
        last_dash_part = base.split('-')[-1]
        m = re.fullmatch(r'es\d+', last_dash_part)
        return m.group(0) if m else None

    for file in os.listdir(input_file_dir):
        if not file.endswith('.xyz'):
            continue
        if file == 'E0s.xyz':
            continue
        if filter_sf and 'es' not in file:
            continue

        parts = file.split('_')
        sample_type = parts[0]
        tail = parts[-1]
        es_key = extract_es_key(tail)
        if es_key is None:
            continue

        head_type = file.split('_')[-1]  # e.g. "molecule-es1.xyz"
        file_path = os.path.join(input_file_dir, file)
        frames = list(read(file_path, index=":"))

        molecules = []
        for t in frames:
            tp = t.copy()
            tp.info["REF_energy"] = t.calc.results["energy"]
            tp.arrays["REF_forces"] = t.calc.results["forces"]
            molecules.append(tp)

        datasets.setdefault(es_key, {}).setdefault((sample_type, head_type), []).extend(molecules)
        samples_dict[sample_type] = samples_dict.get(sample_type, 0) + len(frames)

    # Shuffle
    for es_key in datasets:
        for key in datasets[es_key]:
            random.shuffle(datasets[es_key][key])

    # Duplicate
    if duplicate_data:
        for es_key in datasets:
            for key in datasets[es_key]:
                datasets[es_key][key] *= 2
        for k in list(samples_dict.keys()):
            if k != 'E0s':
                samples_dict[k] *= 2

    if combined:
        # One combined pair per es_key
        for es_key, by_sample in datasets.items():
            combined_data = []
            for _, mols in by_sample.items():
                combined_data.extend(mols)

            num_molecules = len(combined_data)
            num_train = int(train_ratio * num_molecules)

            train_molecules = combined_data[:num_train] + e0s
            val_molecules = combined_data[num_train:] + e0s

            write(os.path.join(output_folder, f'train_{es_key}.xyz'), train_molecules)
            write(os.path.join(output_folder, f'validation_{es_key}.xyz'), val_molecules)
    else:
        # Keep original file naming logic
        for es_key, by_sample in datasets.items():
            for (sample_type, head_type), mols in by_sample.items():
                num_molecules = len(mols)
                num_train = int(train_ratio * num_molecules)

                train_molecules = mols[:num_train] + e0s
                val_molecules = mols[num_train:] + e0s

                write(os.path.join(output_folder, f'train_{sample_type}_{head_type[:-4]}.xyz'), train_molecules)
                write(os.path.join(output_folder, f'validation_{sample_type}_{head_type[:-4]}.xyz'), val_molecules)

    # Save counts
    df = pd.DataFrame(samples_dict.items(), columns=['Sample', 'Number of molecules'])
    df.to_csv(os.path.join(output_folder, 'samples_info.csv'), index=False)


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
        if system_data_type == 'combined':
            combine_split_xyz_files(system_data_input_folder, system_data_output_folder, duplicate_data= True, filter_sf= True, combined= True)
        else:
            combine_split_xyz_files(system_data_input_folder, system_data_output_folder, duplicate_data= True, filter_sf= True, combined= False)
