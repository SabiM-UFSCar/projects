"""
Simulações Ab-initio de Materiais - SAbiM
====================
POSCAR - Handles creation and writing of VASP POSCAR files.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""
import re
from itertools import islice
from pathlib import Path
from utils import logger, log_generate_inputs

POSCAR_FILE_TEMPLATE = "POSCAR_PATTERN"
PATH_FOLDER_TEMPLATE = Path("./vasp_templates/POSCAR")
LINES_TO_MODIFY = {1, 6}


@log_generate_inputs
def run_write_poscar(path_output_folder: str, list_elements: list, space_group: str):
    """
    Write a POSCAR file for VASP calculations.

    Args:
        path_output_folder (str): Directory to save the POSCAR file.
        list_elements (list): List of chemical elements in the structure.
        space_group (str): Space group of the structure.

    Returns:
        bool: True if the POSCAR file was created successfully, False otherwise.

    Raises:
        ValueError: If the input list is empty or does not contain exactly two elements.
        FileNotFoundError: If the template POSCAR file is not found.
    """
    # Validate inputs
    path_poscar_template = PATH_FOLDER_TEMPLATE.joinpath(space_group, POSCAR_FILE_TEMPLATE)
    if not path_poscar_template.exists():
        logger.error(f"Template POSCAR not found at {path_poscar_template.resolve()}")
        raise FileNotFoundError(f"Template POSCAR not found at {path_poscar_template.resolve()}")
    
    template_lines = path_poscar_template.read_text(encoding='utf-8').splitlines()

    element_m, element_q = list(islice(list_elements, 2))

    # Process and modify lines
    output_lines = []
    numbers = None  # To store extracted numbers from line 1
    pattern = re.compile(r"(\d+)")

    for line_num, line in enumerate(template_lines, start=1):
        if line_num in LINES_TO_MODIFY:
            if line_num == 1:
                # Extract numbers from template line 1
                numbers = pattern.findall(line)
                if len(numbers) < 2:
                    raise ValueError("Template POSCAR line 1 missing required numbers")
                new_line = f"{element_m}{numbers[0]} {element_q}{numbers[1]} - (auto generated POSCAR)\n"
                output_lines.append(new_line)
            elif line_num == 6:
                output_lines.append(f"{element_m}   {element_q}\n")
        else:
            output_lines.append(line)

    # Write output file
    try:    
        logger.info(f"Writing POSCAR file for {', '.join(map(str, list_elements))}")
        cleaned_lines_poscar = [line.strip('\n') for line in output_lines]
        path_poscar_file = Path(path_output_folder).joinpath("POSCAR")
        path_poscar_file.write_text('\n'.join(cleaned_lines_poscar), encoding='utf-8')
        logger.info(f"POSCAR file written to {path_poscar_file.resolve()}")
        if numbers:
            logger.info(f"Chemistry formula M: {element_m}{numbers[0]} Q: {element_q}{numbers[1]}")
            logger.info("POSCAR file generated successfully")
            return True
    except IOError as e:
        logger.error(f"Failed to write POSCAR file: {str(e)}")
        raise IOError(f"Failed to write POSCAR file: {str(e)}") from e

    return False