# vasp_io/poscar_write.py
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
import numpy as np
from utils import logger, log_generate_inputs
from config import PATH_FOLDER_TEMPLATE, POSCAR_FILE_TEMPLATE, LINES_TO_MODIFY


@log_generate_inputs
def run_write_poscar(path_output_folder: str, list_elements: list, space_group: str):
    """Generates VASP POSCAR file from template with customized chemistry headers.

    Creates structure input file by:
    1. Loading space group-specific template POSCAR
    2. Customizing element headers using first two elements in input list
    3. Modifying specific lines (system title and element names)
    4. Writing formatted output to target directory

    Args:
        path_output_folder: Output directory path (str or Path-convertible)
        list_elements: Chemical elements for material system (e.g., ['Na','Cl'])
        space_group: Space group identifier for template selection

    Returns:
        True on successful file creation, False otherwise

    Raises:
        FileNotFoundError: If template POSCAR file is missing
        ValueError: For invalid template format or insufficient elements
        IOError: If file writing fails

    Example:
        >>> run_write_poscar('calc_dir', ['Na','Cl'], 'Fm-3m')
        Creates POSCAR in calc_dir with Na-Cl headers
    """
    # Validate template file existence before processing
    # Critical: Required for POSCAR generation workflow
    path_poscar_template = PATH_FOLDER_TEMPLATE.joinpath(space_group, POSCAR_FILE_TEMPLATE)
    if not path_poscar_template.exists():
        logger.error(f"Template POSCAR not found at {path_poscar_template.resolve()}")
        raise FileNotFoundError(f"Template POSCAR not found at {path_poscar_template.resolve()}")
    
    # Read template lines for modification
    template_lines = path_poscar_template.read_text(encoding='utf-8').splitlines()

    # Extract first two elements for material system
    # Note: VASP convention requires ordered element specification
    element_m, element_q = list(islice(list_elements, 2))

    # Initialize output buffer with regex for number extraction
    output_lines = []
    numbers = None  # To store extracted numbers from line 1
    pattern = re.compile(r"(\d+)")

    # Process each template line with custom modifications
    # Why: Only specific lines require element-dependent changes
    for line_num, line in enumerate(template_lines, start=1):
        if line_num in LINES_TO_MODIFY:
            # Line 1: Customize system title with element counts
            if line_num == 1:
                # Extract numeric identifiers from template (e.g., "4" in "Na4")
                numbers = pattern.findall(line)
                if len(numbers) < 2:
                    raise ValueError("Template POSCAR line 1 missing required numbers")
                # Format new title line with elements and extracted counts
                new_line = f"{element_m}{numbers[0]} {element_q}{numbers[1]} - (auto generated POSCAR)\n"
                output_lines.append(new_line)
            # Line 6: Insert element names in VASP-required order
            elif line_num == 6:
                output_lines.append(f"{element_m}   {element_q}\n")
        # Preserve unmodified template lines
        else:
            output_lines.append(line)

    # Write processed content to output file
    try:
        logger.info(f"Writing POSCAR file for {', '.join(map(str, list_elements))}")
        # Clean line breaks for consistent POSCAR formatting
        cleaned_lines_poscar = [line.strip('\n') for line in output_lines]
        path_poscar_file = Path(path_output_folder).joinpath("POSCAR")
        path_poscar_file.write_text('\n'.join(cleaned_lines_poscar), encoding='utf-8')
        logger.info(f"POSCAR file written to {path_poscar_file.resolve()}")
        # Log final chemical formula for verification
        if numbers:
            logger.info(f"Chemistry formula M: {element_m}{numbers[0]} Q: {element_q}{numbers[1]}")
            logger.info("POSCAR file generated successfully")
            return True
    except IOError as e:
        logger.error(f"Failed to write POSCAR file: {str(e)}")
        raise IOError(f"Failed to write POSCAR file: {str(e)}") from e

    return False

@log_generate_inputs
def read_poscar_vectors(path_poscar: Path):
    if not path_poscar.exists():
        raise FileNotFoundError(f"POSCAR file not found at {path_poscar.resolve()}")
    
    with path_poscar.open(encoding='utf-8') as file:
        try:
            cflat = file.readline().strip()
            scale = np.float64(file.readline().strip())
            a1 = np.array(file.readline().strip().split(), dtype=np.float64)
            a2 = np.array(file.readline().strip().split(), dtype=np.float64)
            a3 = np.array(file.readline().strip().split(), dtype=np.float64)
            return cflat, scale, a1, a2, a3
        except Exception as e:
            raise ValueError(f"Error reading POSCAR vectors: {str(e)}") from e
