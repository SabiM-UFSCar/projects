# vasp_init/vasp_setup.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
VASP - This script is designed to generate input files for VASP calculations.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

from pathlib import Path
from incar_writer import run_write_incar
from kpoints_writer import run_kpoints_writer
from poscar_writer import run_write_poscar
from Monochalcogenides2D.common.config import PATH_FOLDER_OUTPUT, LIST_MQ, LIST_SP
from Monochalcogenides2D.common.utils import init_logger, task_generate_log, progress_bar_show, get_mq_elements


@task_generate_log
def run_generate_inputs(name_output_folder: str):
    """Orchestrates VASP input generation for multiple space groups and material systems.

    Creates nested directory structure and generates POSCAR/INCAR files
    for all combinations of space groups in LIST_SP and materials in LIST_MQ.
    Serves as the top-level workflow controller for input file generation.

    Args:
        name_output_folder: Name for directory for output file hierarchy

    Returns:
        None (writes files to disk)

    Raises:
        OSError: If directory creation fails
        RuntimeError: Propagated from file generation functions

    Example:
        >>> run_generate_inputs('vasp_simulations')
        Generates input files for all material/space group combinations
    """
    # Initialize root output directory with safe creation
    # Critical: Ensures base path exists before nested generation
    path_output = PATH_FOLDER_OUTPUT.joinpath(name_output_folder)
    path_output.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory set to: {path_output.resolve()}\n")

    system_count = 0
    progress_bar_show(system_count)
    # Process each space group in predefined list
    # Why: Different crystal structures require distinct templates
    for sp in LIST_SP:
        # Initialize path placeholder for current space group
        path_output_sp = ""

        # Process each material system in predefined list
        # Note: Materials are represented as string identifiers (e.g., "NaCl")
        for mq in LIST_MQ:
            # Create material-specific subdirectory under space group
            # Structure: root/space_group/material_system/
            path_output_sp = path_output.joinpath(sp, mq)
            path_output_sp.mkdir(parents=True, exist_ok=True)
            logger.info(f"Processing space group: {sp} with material: {mq}")

            # Generate POSCAR file with space-group-appropriate template
            # Note: get_mq_elements() converts material ID to element list
            if run_write_poscar(path_output_sp, get_mq_elements(mq), sp):
                logger.info(f"POSCAR file created successfully for {mq} in space group {sp}.")
            else:
                logger.info(f"Failed to create POSCAR file for {mq} in space group {sp}.")
                raise RuntimeError(f"POSCAR generation failed for {mq} in space group {sp}.")

            # Generate matching INCAR file with material-specific parameters
            # Critical: Must run after POSCAR for folder structure consistency
            run_write_incar(path_output_sp, get_mq_elements(mq))

            # Generate matching KPOINTS file with material-specific parameters
            # Critical: Must run after POSCAR for folder structure consistency
            run_kpoints_writer(path_output_sp)

            system_count += 1
            progress_bar_show(system_count)
            logger.info(f"Completed input generation for {mq} in space group {sp}. Total systems: {system_count}\n\n")



if __name__ == "__main__":
    logger = init_logger(task_name = "VASP_SETUP", level = "INFO")
    run_generate_inputs("vasp_simulations")
else:
    from loguru import logger