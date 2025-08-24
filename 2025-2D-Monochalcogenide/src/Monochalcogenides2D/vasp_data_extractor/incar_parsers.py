# vasp_data_extractor/incar_parsers.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
INCAR - Parsing information from INCAR file.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import os
import sys


def read_incar(path_file):
    """
    Read and preprocess all non-empty lines from an INCAR file.
    
    Reads an INCAR file (VASP input parameters), removes empty lines and
    whitespace, and returns a list of cleaned lines for further processing.

    Args:
        path_file (str): Path to the INCAR file to read.

    Returns:
        list: Cleaned lines from the INCAR file without empty lines.

    Raises:
        SystemExit: If the specified file does not exist.
    """
    # Validate file existence before attempting to read
    if not os.path.isfile(path_file):
        sys.exit(f'File: {path_file} does not exist')

    # Read and clean file contents in one operation
    with open(path_file, 'r') as incar_file:
        lines_incar = incar_file.readlines()
        # Remove whitespace and filter out empty lines
        lines_incar = [line.strip() for line in lines_incar if line.strip()]

    return lines_incar


def create_incar_dict_flags(path_file):
    """
    Parse INCAR file into a dictionary of parameter key-value pairs.
    
    Extracts all non-comment lines from an INCAR file and converts them
    into a dictionary format for easy parameter access and modification.
    Skips lines starting with '#' (comments).

    Args:
        path_file (str): Path to the INCAR file to parse.

    Returns:
        dict: Dictionary containing all INCAR parameters as key-value pairs.

    Raises:
        SystemExit: If the specified file does not exist.
    """
    # Validate file existence before processing
    if not os.path.isfile(path_file):
        sys.exit(f'File: {path_file} does not exist')
    
    dict_flags_incar = {}
    # Get cleaned lines from INCAR file
    lines_incar = read_incar(path_file)
    
    # Process each line to extract parameters, ignoring comments
    for line in lines_incar:
        if not line.startswith('#'):
            # Convert line to dictionary entry and update main dictionary
            dict_flags_incar.update(pattern_to_dict(line))

    return dict_flags_incar


def pattern_to_dict(pattern_string: str) -> dict:
    """
    Convert a single INCAR parameter line to a dictionary entry.
    
    Parses a string in the format "KEY = VALUE" into a dictionary
    with KEY as the key and VALUE as the corresponding value.

    Args:
        pattern_string (str): INCAR parameter line to parse.

    Returns:
        dict: Single-key dictionary containing the parsed parameter.

    Example:
        >>> pattern_to_dict("EDIFF = 1e-6")
        {'EDIFF': '1e-6'}
    """
    if pattern_string is not None:
        # Clean input and split into key-value parts
        pattern_string = pattern_string.strip()
        parts = pattern_string.split('=')
        # Return dictionary with stripped key and value
        return {parts[0].strip(): parts[1].strip()}


def dict_to_pattern_incar(dict_incar: dict) -> str:
    """
    Convert a dictionary of parameters back to INCAR file format.
    
    Reconstructs the INCAR file content from a dictionary of parameters
    using standard "KEY = VALUE" formatting with newline separation.

    Args:
        dict_incar (dict): Dictionary of INCAR parameters to convert.

    Returns:
        str: Formatted INCAR file content as a single string.

    Example:
        >>> dict_to_pattern_incar({'EDIFF': '1e-6', 'NSW': '500'})
        "EDIFF = 1e-6\nNSW = 500\n"
    """
    pattern_string = ''
    # Rebuild INCAR format from dictionary entries
    for key, value in dict_incar.items():
        pattern_string += f'{key} = {value}\n'
    return pattern_string


def create_incar_file_from_dict(path_file, incar_dict_flags: dict):
    """
    Write a new INCAR file from a dictionary of parameters.
    
    Generates a complete INCAR file from a parameter dictionary,
    overwriting any existing file at the specified path.

    Args:
        path_file (str): Destination path for the new INCAR file.
        incar_dict_flags (dict): Dictionary of parameters to write.

    Example:
        >>> create_incar_file_from_dict('INCAR', {'EDIFF': '1e-6'})
        # Creates INCAR file with "EDIFF = 1e-6"
    """
    # Convert dictionary to INCAR format string
    lines_incar_file = dict_to_pattern_incar(incar_dict_flags)
    # Write complete content to file
    with open(path_file, 'w') as incar_file:
        incar_file.writelines(lines_incar_file)