import multiprocessing
import os
import re

from CORE import CONST as C
from VASPStructuresFile.VASPFileBuilder import VASPFileCreator


def create_folder_initial_structure(path_folder):
    """
    Create the initial folder structure for simulation files and generate simulation files.

    :param path_folder: Path of the root directory for the folder structure.
    """
    # Initialize lists for folders and additional arguments
    list_folders = []
    additional_args_list = []
    # Iterate through chemical compounds
    for unitary_compounds in C.LIST_CHEMICAL_COMPOUNDS:
        try:
            # Create folder for each chemical compound
            _path_unitary_compounds = os.path.join(str(path_folder), unitary_compounds)
            os.makedirs(_path_unitary_compounds, exist_ok=True)

            # Iterate through structures
            for structure in C.LIST_STRUCTURES:
                try:
                    # Create folder for each structure
                    _path_structure = os.path.join(_path_unitary_compounds, structure)
                    os.makedirs(_path_structure, exist_ok=True)

                    # Set patterns, ratio factor, and elements
                    _poscar_pattern = 'POSCAR_' + str(structure)
                    _incar_pattern = 'INCAR_STRESS_RELAXATION'
                    ratio_factor = 2.0
                    elements = re.findall('[A-Z][^A-Z]*', unitary_compounds)

                    # Append additional arguments for generating files
                    additional_args_list.append((_incar_pattern, _poscar_pattern, elements, structure, ratio_factor))
                    # Append folder to the list
                    list_folders.append(_path_structure)
                except FileExistsError:
                    print('error')
        except FileExistsError:
            print('error')

    # Create arguments list for multiprocessing
    args_list = [(folder, *additional_args) for folder, additional_args in zip(list_folders, additional_args_list)]

    # Execute multiprocessing to generate files
    with multiprocessing.Pool() as pool:
        results = pool.map(process_for_generating_files, args_list)
        results_with_args = list(zip(args_list, results))

        # Print results for each argument
        for arg, result in results_with_args:
            print("Argumento:", arg)
            print("Results:", result)
            print()

        # Close and join the pool
        pool.close()
        pool.join()


def process_for_generating_files(args):
    """
    Process for generating simulation files based on provided arguments.

    :param args: Tuple containing the following elements:
                 - path_folder: Path of the folder.
                 - incar_pattern: Pattern for INCAR file.
                 - poscar_pattern: Pattern for POSCAR file.
                 - elements: List of chemical elements.
                 - structure: Structure of the simulation.
                 - ratio_factor: Ratio factor for simulation.

    :return: True if the process is successful, False otherwise.
    """
    path_folder, incar_pattern, poscar_pattern, elements, structure, ratio_factor = args
    generate_files = VASPFileCreator(path_folder, incar_pattern, poscar_pattern)
    generate_files.set_elements(elements)
    generate_files.set_structure(structure)
    generate_files.set_ratio_factor(2.0)
    list_elements = ['Sn', 'In']
    generate_files.set_list_potcar_extra_folder(list_elements, '_d_GW')
    generate_files.build_simulation_files()
    return True
