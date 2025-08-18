# vasp_io/incar_writer.py
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
from config import (INCAR_FILE_TEMPLATE, PATH_FOLDER_POTPAW,
                    LIST_POTCAR_D_GW, RATIO_FACTOR)

@log_generate_inputs
def run_write_incar(folder_output: Path, mq: list):
    """Generates VASP INCAR and POTCAR files for a binary material system.

    This function creates VASP input files by:
    1. Retrieving POTCAR data for two elements in a material system
    2. Calculating ENCUT based on highest element ENMAX
    3. Modifying template INCAR with system name and calculated ENCUT
    4. Writing concatenated POTCAR file for both elements

    Args:
        folder_output: Output directory Path object for writing files
        mq: List containing two element symbols [M, Q] (e.g., ['Na', 'Cl'])

    Returns:
        None (writes INCAR and POTCAR files to disk)

    Raises:
        FileNotFoundError: If POTCAR files for elements are missing
        OSError: If file writing operations fail

    Example:
        >>> run_write_incar(Path('calc_dir'), ['Na', 'Cl'])
        Creates INCAR and POTCAR in calc_dir with Na-Cl parameters
    """
    # Define output file paths for INCAR and POTCAR
    incar_output = folder_output.joinpath("INCAR")
    potcar_output = folder_output.joinpath("POTCAR")

    # Retrieve POTCAR metadata and content for both elements
    # Critical: Required to determine ENCUT and build POTCAR file
    try:
        titel_m, date_potcar_m, enmax_m, zval_m, content_file_m = get_potcar_info(mq[0])
        titel_q, date_potcar_q, enmax_q, zval_q, content_file_q = get_potcar_info(mq[1])
    except FileNotFoundError as e:
        logger.error(f"Error retrieving POTCAR info: {e}")
        raise
    
    # Determine ENCUT using highest element ENMAX with safety factor
    # Note: Uses same value when ENMAX are equal for consistency
    if enmax_m > enmax_q:
        incar_encut = enmax_m * RATIO_FACTOR
    elif enmax_q > enmax_m:
        incar_encut = enmax_q * RATIO_FACTOR
    else:
        incar_encut = enmax_m * RATIO_FACTOR

    # Load template INCAR file lines for modification
    incar_template = INCAR_FILE_TEMPLATE.read_text(encoding='utf-8').splitlines()
    
    # Combine POTCAR contents and write to output file
    # Order matters: First element (M) then second element (Q)
    content_file_potcar = content_file_m + content_file_q
    potcar_output.write_bytes(content_file_potcar)
    logger.info(f"POTCAR file created successfully at {potcar_output.resolve()}")
    
    # Modify template INCAR lines with system-specific parameters
    logger.info("Altering INCAR file...")
    incar_lines_content = []
    for line_number, lines in enumerate(incar_template, start=1):
        # Line 1: Add material system comment header
        if line_number == 1:
            new_line = "#SYSTEM " + mq[0] + " " + mq[1] + " - (auto generated INCAR)\n"
            incar_lines_content.append(new_line)
        # Line 4: Insert calculated ENCUT value
        elif line_number == 4:
            new_line = "ENCUT   =   " + str(incar_encut) + "\n"
            incar_lines_content.append(new_line)
        # Preserve all other template lines unchanged
        else:
            incar_lines_content.append(lines)

    # Write cleaned INCAR lines to output file
    cleaned_lines_incar = [line.strip('\n') for line in incar_lines_content]
    incar_output.write_text('\n'.join(cleaned_lines_incar), encoding='utf-8')
    logger.info(f"INCAR file written to {incar_output.resolve()}")

@log_generate_inputs
def potpaw_folder_for_element(element: str) -> Path:
    """Finds the appropriate POTCAR folder path for a given element.

    Determines the correct POTCAR directory path by considering special
    handling requirements for certain elements. Uses GW pseudopotential
    directories with '_d_GW' suffix for specific elements in LIST_POTCAR_D_GW,
    standard '_GW' suffix for others.

    Args:
        element: Chemical symbol of the element (e.g., 'Na', 'Fe')

    Returns:
        Path to POTCAR file within the appropriate element directory

    Raises:
        FileNotFoundError: If no matching POTCAR directory exists
        NotADirectoryError: If PATH_FOLDER_POTPAW contains non-directory items

    Example:
        >>> potpaw_folder_for_element('Fe')
        Path('/pseudopotentials/Fe_d_GW/POTCAR')
    """
    # List all directories in the main POTPAW folder
    # Critical: Identifies available element pseudopotential versions
    potcar_list_folders = [folder.name for folder in PATH_FOLDER_POTPAW.iterdir() if folder.is_dir()]
    
    # Default folder naming convention for standard elements
    folder_element_name = f"{element}_GW"

    # Special handling for elements requiring d-electron treatment
    # Note: LIST_POTCAR_D_GW contains elements needing '_d_GW' suffix
    if element in LIST_POTCAR_D_GW:
        folder_element_name = f"{element}_d_GW"

    # Verify the determined folder exists in available directories
    # Critical: Ensures valid POTCAR path before returning
    if folder_element_name in potcar_list_folders:
        return PATH_FOLDER_POTPAW.joinpath(folder_element_name, "POTCAR")


@log_generate_inputs
def get_potcar_info(element: str) -> str:
    """Retrieves POTCAR file metadata and content for a specified element.

    Reads pseudopotential file for given element, extracts key parameters
    (TITEL, date, ENMAX, ZVAL) and returns both metadata and file content.
    Uses memory-mapping for efficient parsing of large POTCAR files.

    Args:
        element: Chemical symbol of target element (e.g., 'Si', 'O')

    Returns:
        tuple: (TITEL, date, ENMAX, ZVAL, raw_content) containing:
            TITEL: Elemental descriptor string
            date: POTCAR creation date
            ENMAX: Maximum cutoff energy (eV)
            ZVAL: Valence electrons
            raw_content: Binary POTCAR file contents

    Raises:
        FileNotFoundError: If element's POTCAR file is missing
        OSError: For file access/permission issues
        ValueError: If POTCAR parsing fails

    Example:
        >>> get_potcar_info('Si')
        ('PAW_PBE Si 05Jan2001', '05Jan2001', 245.3, 4.0, b'...')
    """
    # Retrieve element-specific POTCAR file path
    # Critical: Depends on external path resolution logic
    path_potcar_element = potpaw_folder_for_element(element)

    # Read POTCAR content and create memory map for efficient parsing
    # Why: mmap enables large file handling without full loading
    with open(path_potcar_element, 'rb') as potcar_file:
        # Store raw content for POTCAR reassembly
        content_file = potcar_file.read()
        # Create read-only memory map for metadata extraction
        file_map = mmap.mmap(potcar_file.fileno(), 0, access=mmap.ACCESS_READ)

    # Extract key pseudopotential parameters from memory-mapped file
    # Note: search_potcar_files contains parsing logic for VASP format
    titel, date_potcar, enmax, zval = search_potcar_files(file_map)

    # Release memory map resources immediately after use
    file_map.close()

    return titel, date_potcar, enmax, zval, content_file


@log_generate_inputs
def search_potcar_files(file_map):
    """Extracts key metadata from POTCAR files using regex pattern matching.

    Parses memory-mapped POTCAR files to retrieve critical pseudopotential parameters:
    TITEL descriptor, creation date, ENMAX cutoff energy, and ZVAL electron count.
    Uses efficient memory mapping and line extraction for large file handling.

    Args:
        file_map: Memory-mapped pseudopotential file object (mmap)

    Returns:
        tuple: (titel_line, formatted_titel, enmax_value, zval_value) containing:
            titel_line: Raw TITEL line content (str)
            formatted_titel: Processed elemental descriptor (str)
            enmax_value: Maximum cutoff energy (float)
            zval_value: Valence electron count (float)

    Raises:
        AttributeError: If regex patterns fail to match expected formats
        UnicodeDecodeError: If binary-to-text conversion fails

    Example:
        >>> with open('POTCAR', 'rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        >>>     search_potcar_files(mm)
        ('PAW_PBE Fe 06Sep2000', 'Fe', 268.2, 8.0)
    """
    # Pre-compile byte patterns for efficient searching
    # Why: Avoid recompiling patterns during file scanning
    pattern_search_titel = re.compile(b'TITEL')
    pattern_search_enmax = re.compile(b'ENMAX')
    pattern_search_zval = re.compile(b'ZVAL')

    # Initialize return values to handle missing data cases
    string_titel, data_titel_file, enmax_float, zval_float = None, None, None, None

    # Extract TITEL line containing elemental descriptor
    # Critical: Identifies pseudopotential type and version
    for result in pattern_search_titel.finditer(file_map):
        start_r = result.start()
        end_r = result.end()

        # Isolate full line containing the TITEL marker
        line_start = file_map.rfind(b'\n', 0, start_r) + 1
        line_end = file_map.find(b'\n', end_r)
        string_titel = file_map[line_start:line_end].decode('utf-8')
        
        # Extract and format elemental identifier (e.g., '12Fe3' -> 'Fe')
        data_file_search = re.compile(r'(\d{1,}[A-z]{3}\d{1,})')
        data_string = re.search(data_file_search, string_titel)
        data_potcat = data_string.group(1)
        data_titel_file = return_data_formatted_titel(data_potcat)

    # Retrieve ENMAX value - critical for energy cutoff calculations
    # Why: Determines basis set size in DFT simulations
    for result in pattern_search_enmax.finditer(file_map):
        start_r = result.start()
        end_r = result.end()

        # Extract full ENMAX parameter line
        line_start = file_map.rfind(b'\n', 0, start_r) + 1
        line_end = file_map.find(b'\n', end_r)
        string_enmax = file_map[line_start:line_end].decode('utf-8')
        
        # Capture floating-point value after ENMAX marker
        enmax_search_value = r'ENMAX\s*=\s*(\d+.\d+)'
        enmax_values = re.search(enmax_search_value, string_enmax)
        if enmax_values:
            enmax_float = float(enmax_values.group(1))

    # Extract ZVAL (valence electron count)
    # Why: Essential for charge neutrality calculations
    for result in pattern_search_zval.finditer(file_map):
        start_r = result.start()
        end_r = result.end()
        
        # Isolate full ZVAL parameter line
        line_start = file_map.rfind(b'\n', 0, start_r) + 1
        line_end = file_map.find(b'\n', end_r)
        string_zval = file_map[line_start:line_end].decode('utf-8')
        
        # Capture floating-point value after ZVAL marker
        zval_search_value = r'ZVAL\s*=\s*(\d+.\d+)'
        zval_values = re.search(zval_search_value, string_zval)
        if zval_values:
            zval_float = float(zval_values.group(1))

    return string_titel, data_titel_file, enmax_float, zval_float
