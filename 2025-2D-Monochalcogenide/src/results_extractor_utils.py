import json
import multiprocessing
import os

from CORE import CONST as C
from CORE import utils
from ReportGeneration import JsonBuilder
from VASPDataExtractors import ResultsExtractor


def list_folders_for_stress_relaxation():
    """
    Retrieve folders containing stress relaxation data.

    :return: List of folders containing stress relaxation data.
    """
    list_folders_stress = utils.list_first_folders(C.PATH_FOLDER_STRESS_RELAXATION)
    result_path = utils.expand_folders_path(list_folders_stress, C.PATH_FOLDER_STRESS_RELAXATION, 'results')
    list_all_folders_results = []
    for path in result_path:
        last_folders = utils.list_last_folders_recursively(path)
        list_all_folders_results.extend(last_folders)

    return list_all_folders_results


def generate_json_result_stress_relaxation(file_name_json):
    """
    Generate JSON file containing results of stress relaxation simulations.

    This function retrieves folders for stress relaxation simulations, processes each folder in parallel,
    and generates a JSON file containing the extracted data.

    :return: None
    """
    list_folders = list_folders_for_stress_relaxation()
    pool = multiprocessing.Pool()
    results = pool.map(process_folder, list_folders)
    name_json_file = os.path.join(C.PATH_FOLDER_JSON_FILES, file_name_json)
    JsonBuilder.generate_json_from_list_dicts(results, name_json_file)


def generate_json_result_static_force(file_name_json):
    """
    Generate JSON file containing results of static simulation for ENCUT of ENMAX*1.125. simulations.

    This function retrieves folders for static simulations, processes each folder in parallel,
    and generates a JSON file containing the extracted data.

    :return: None
    """
    list_folders = utils.list_last_folders_recursively(C.PATH_FOLDER_STATIC_TOTAL_ENERGY)
    pool = multiprocessing.Pool()
    results = pool.map(process_folder, list_folders)
    name_json_file = os.path.join(C.PATH_FOLDER_JSON_FILES, file_name_json)
    JsonBuilder.generate_json_from_list_dicts(results, name_json_file)


def process_folder(folder):
    """
    Process a folder containing simulation data files.

    :param folder: Path to the folder containing simulation data.

    :return: Extracted simulation data. (list)
    """
    extractor = ResultsExtractor.ResultsExtractor(folder)
    return extractor.await_validation_simulation_files()


def generate_relative_energy_and_order_for_element(json_file, output_json_file_name):
    """
    Generate relative energy and order information for chemical elements from a JSON file.

    This function reads data from the specified JSON file, calculates the relative energy
    and order for each chemical element, and saves the results to a new JSON file.

    :param json_file: The path to the input JSON file containing simulation data.
    :param output_json_file_name: The name of the output JSON file to be generated.

    :return: None

    Examples Usage:
    generate_relative_energy_and_order_for_element('input_data.json', 'output_results.json')

    Note:
    This function processes the simulation data stored in the input JSON file
    and generates a new JSON file containing the calculated relative energy
    and order information for each chemical element.

    """
    with open(json_file, 'r') as json_file:
        data = json.load(json_file)

    static_energy_relative_energy = []
    for unitary_chemical_compound in C.LIST_CHEMICAL_COMPOUNDS:
        list_chemical_compounds = []
        for entry in data:
            if entry['unitary_chemical_compound'] == unitary_chemical_compound:
                list_chemical_compounds.append(entry)
        static_energy_relative_energy.append(calculate_relative_energy(list_chemical_compounds))

    JsonBuilder.generate_json_from_list_dicts(static_energy_relative_energy, output_json_file_name)


def calculate_relative_energy(list_chemical_compounds):
    """
    Calculate the relative energy for a list of chemical compounds.

    This function calculates the relative energy for each chemical compound in
    the provided list based on the minimum energy structure found within the list.
    The relative energy is computed as the difference between the energy of each
    structure and the minimum energy structure, scaled by a factor of 1000.

    :param list_chemical_compounds: A list containing dictionaries representing
            the chemical compounds, where each dictionary contains information about the
            chemical structure and its energy.

    :return: A list of dictionaries containing the chemical structures along with their
            computed relative energies.

    Examples Usage:
    data = [{'structure': 'Aem2', 'e_unitary': -20.0},
           {'structure': 'P6m2', 'e_unitary': -19.5},
           {'structure': 'P3m1_alpha', 'e_unitary': -21.0}]
    calculate_relative_energy(data)
    [{'structure': 'Aem2', 'e_unitary': -20.0, 'e_relative': 0.0},
     {'structure': 'P6m2', 'e_unitary': -19.5, 'e_relative': 500.0},
     {'structure': 'P3m1_alpha', 'e_unitary': -21.0, 'e_relative': -1000.0}]

    Note:
    This function iterates through the list of chemical compounds to determine
    the minimum energy structure, and then computes the relative energy for each
    structure based on this minimum energy.

    """
    min_energy_structure = min(d['e_unitary'] for d in list_chemical_compounds)
    list_dicts_order = sorted(list_chemical_compounds, key=lambda x: x['e_unitary'])
    for structure in list_dicts_order:
        structure['e_relative'] = 1000 * (structure['e_unitary'] - min_energy_structure)
    return list_dicts_order
