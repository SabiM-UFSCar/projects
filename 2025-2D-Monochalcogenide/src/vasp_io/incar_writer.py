"""
Simulações Ab-initio de Materiais - SAbiM
====================
INCAR - Handles creation and writing of VASP INCAR files.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import re
import mmap
from pathlib import Path
from utils import logger, log_generate_inputs, return_data_formatted_titel

PATH_FOLDER_POTPAW = Path("potpaw_folder")
LIST_POTCAR_D_GW = ['Sn', 'In']
RATIO_FACTOR = 2.0
INCAR_FILE_TEMPLATE = Path("./vasp_templates/INCAR_PATTERN")


@log_generate_inputs
def run_write_incar(folder_output: Path, mq: list):
    """
    Write an INCAR file for VASP calculations.

    This function generates an INCAR file based on a template and modifies it
    according to the specified parameters.

    Returns:
        None
    """

    incar_output = folder_output.joinpath("INCAR")
    potcar_output = folder_output.joinpath("POTCAR")

    # Get POTCAR information for each element in the material
    try:
        titel_m, date_potcar_m, enmax_m, zval_m, content_file_m = get_potcar_info(mq[0])
        titel_q, date_potcar_q, enmax_q, zval_q, content_file_q = get_potcar_info(mq[1])
    except FileNotFoundError as e:
        logger.error(f"Error retrieving POTCAR info: {e}")
        raise
    
    # Determine which one has the highest maximum energy
    if enmax_m > enmax_q:
        incar_encut = enmax_m * RATIO_FACTOR
    elif enmax_q > enmax_m:
        incar_encut = enmax_q * RATIO_FACTOR
    else:
        incar_encut = enmax_m * RATIO_FACTOR

    # Read the template INCAR file
    incar_template = INCAR_FILE_TEMPLATE.read_text(encoding='utf-8').splitlines()
    
    # create potcar file for elements first element m , second element q
    content_file_potcar = content_file_m + content_file_q
    potcar_output.write_bytes(content_file_potcar)
    logger.info(f"POTCAR file created successfully at {potcar_output.resolve()}")
    
    logger.info("Altering INCAR file...")
    incar_lines_content = []
    for line_number, lines in enumerate(incar_template, start=1):
        if line_number == 1:
            new_line = "#SYSTEM " + mq[0] + " " + mq[1] + " - (auto generated INCAR)\n"
            incar_lines_content.append(new_line)
        elif line_number == 4:
            new_line = "ENCUT   =   " + str(incar_encut) + "\n"
            incar_lines_content.append(new_line)
        else:
            incar_lines_content.append(lines)

    cleaned_lines_incar = [line.strip('\n') for line in incar_lines_content]
    incar_output.write_text('\n'.join(cleaned_lines_incar), encoding='utf-8')
    logger.info(f"POSCAR file written to {incar_output.resolve()}")


@log_generate_inputs
def potpaw_folder_for_element(element: str) -> Path:
    potcar_list_folders = [folder.name for folder in PATH_FOLDER_POTPAW.iterdir() if folder.is_dir()]
    folder_element_name = f"{element}_GW"

    if element in LIST_POTCAR_D_GW:
        # For elements that require a specific folder structure
        folder_element_name = f"{element}_d_GW"

    if folder_element_name in potcar_list_folders:
        return PATH_FOLDER_POTPAW.joinpath(folder_element_name, "POTCAR")


@log_generate_inputs
def get_potcar_info(element: str) -> str:
    path_potcar_element = potpaw_folder_for_element(element)

    with open(path_potcar_element, 'rb') as potcar_file:
        content_file = potcar_file.read()
        file_map = mmap.mmap(potcar_file.fileno(), 0, access=mmap.ACCESS_READ)

    titel, date_potcar, enmax, zval = search_potcar_files(file_map)

    file_map.close()

    return titel, date_potcar, enmax, zval, content_file


def search_potcar_files(file_map):
    """
    Search and extract TITEL, ENMAX, and ZVAL information from a POTCAR file mapping.

    This function searches for specific patterns (TITEL, ENMAX, ZVAL) in a binary file map,
    extracts the relevant information, and returns formatted data.

    Args:
        file_map (bytes): Binary content of the POTCAR file to be searched.

    Returns:
        tuple: A tuple containing three elements:
            - data_titel_file (str): Formatted TITEL information (e.g., 'Fe_pv').
            - enmax_float (float): The ENMAX value found in the file.
            - zval_float (float): The ZVAL value found in the file.
            Any of these may be None if the corresponding pattern isn't found.
    """
    # Compile regex patterns for the three search targets
    pattern_search_titel = re.compile(b'TITEL')
    pattern_search_enmax = re.compile(b'ENMAX')
    pattern_search_zval = re.compile(b'ZVAL')

    # Initialize return values as None (in case patterns aren't found)
    string_titel, data_titel_file, enmax_float, zval_float = None, None, None, None

    # Titel search
    for result in pattern_search_titel.finditer(file_map):
        # Find the start and end of the matched pattern
        start_r = result.start()
        end_r = result.end()

        # Extract the entire line containing the pattern
        line_start = file_map.rfind(b'\n', 0, start_r) + 1
        line_end = file_map.find(b'\n', end_r)
        string_titel = file_map[line_start:line_end].decode('utf-8')
        
        # Search for the POTCAR data pattern (e.g., '12Fe3')
        data_file_search = re.compile(r'(\d{1,}[A-z]{3}\d{1,})')
        data_string = re.search(data_file_search, string_titel)
        data_potcat = data_string.group(1)
        data_titel_file = return_data_formatted_titel(data_potcat)

    # ENMAX search
    for result in pattern_search_enmax.finditer(file_map):
        start_r = result.start()
        end_r = result.end()

        # Extract the entire line containing the pattern
        line_start = file_map.rfind(b'\n', 0, start_r) + 1
        line_end = file_map.find(b'\n', end_r)
        string_enmax = file_map[line_start:line_end].decode('utf-8')
        
        # Search for the ENMAX value (e.g., 'ENMAX = 123.45')
        enmax_search_value = r'ENMAX\s*=\s*(\d+.\d+)'
        enmax_values = re.search(enmax_search_value, string_enmax)
        if enmax_values:
            enmax_float = float(enmax_values.group(1))

    # ZVAL search
    for result in pattern_search_zval.finditer(file_map):
        start_r = result.start()
        end_r = result.end()
        
        # Extract the entire line containing the pattern
        line_start = file_map.rfind(b'\n', 0, start_r) + 1
        line_end = file_map.find(b'\n', end_r)
        string_zval = file_map[line_start:line_end].decode('utf-8')
        
        # Search for the ZVAL value (e.g., 'ZVAL = 12.00')
        zval_search_value = r'ZVAL\s*=\s*(\d+.\d+)'
        zval_values = re.search(zval_search_value, string_zval)
        if zval_values:
            zval_float = float(zval_values.group(1))

    return string_titel, data_titel_file, enmax_float, zval_float

get_potcar_info('Sn')
