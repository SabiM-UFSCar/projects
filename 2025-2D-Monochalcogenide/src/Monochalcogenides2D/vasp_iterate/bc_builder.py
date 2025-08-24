# vasp_iterate/bc_builder.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
Bader Charger - Handles creation and writing of VASP input files for Bader Charge Analysis.

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import shutil
from pathlib import Path
from Monochalcogenides2D.common.config import LIST_MQ, LIST_SP, LIST_ORDERED_BC_TAGS, PATH_FOLDER_OUTPUT
from Monochalcogenides2D.common.utils import init_logger, task_generate_log, progress_bar_show, order_dict_by_list
from Monochalcogenides2D.vasp_data_extractor import incar_parsers, outcar_parsers


@task_generate_log
def generate_bader_input_files(path_input_base: Path, name_output_bc: str):
    """
    Generates Bader charge analysis input files from VASP outputs for multiple material systems.

    Processes all combinations of space groups (LIST_SP) and materials (LIST_MQ) by:
    1. Creating organized directory structures
    2. Copying essential VASP calculation files (POSCAR, POTCAR, INCAR, KPOINTS)
    3. Updating INCAR files with Bader-specific grid parameters from OUTCAR
    4. Tracking progress with logging and visual progress bars

    Args:
        path_input_base (Path): Base directory containing source VASP files organized as /material/space_group/
        name_output_bc (str): Name of directory where Bader input files will be organized as /space_group/material/

    Raises:
        FileNotFoundError: If source directory for specific material/space group is missing
        OSError: If file operations (copying/directory creation) fail

    Notes:
        Requires predefined LIST_MQ (materials) and LIST_SP (space groups) lists
        Depends on external functions: outcar_parsers.get_number_grid, update_incar_bc, progress_bar_show
    """

    path_output_bc = PATH_FOLDER_OUTPUT.joinpath(name_output_bc)

    system_count = 0
    progress_bar_show(system_count)
    for mq in LIST_MQ:
        # Initialize path placeholder for current space group
        path_output_sp = ""
        path_bc = ""
        path_bc = path_input_base.joinpath(mq)
        # Process each material system in predefined list
        # Note: Materials are represented as string identifiers (e.g., "NaCl")
        for sp in LIST_SP:
            # Create material-specific subdirectory under space group
            # Structure: root/space_group/material_system/
            path_output_sp = path_output_bc.joinpath(sp, mq)
            path_output_sp.mkdir(parents=True, exist_ok=True)
            
            path_bc_sp = path_bc.joinpath(sp)
            logger.info(f"Processing space group: {sp} with material: {mq}")

            if path_bc_sp.is_dir():
                # Copy necessary VASP input files from base directory
                shutil.copy2(path_bc_sp.joinpath("POSCAR"), path_output_sp.joinpath("POSCAR"))
                shutil.copy2(path_bc_sp.joinpath("POTCAR"), path_output_sp.joinpath("POTCAR"))
                shutil.copy2(path_bc_sp.joinpath("INCAR"), path_output_sp.joinpath("INCAR"))
                shutil.copy2(path_bc_sp.joinpath("KPOINTS"), path_output_sp.joinpath("KPOINTS"))
                logger.info(f"Copied VASP input files to {path_output_sp.resolve()}")
            else:
                logger.warning(f"Base path for Bader charge files does not exist: {path_bc_sp.resolve()}") 
                raise FileNotFoundError(f"Base path for Bader charge files does not exist: {path_bc_sp.resolve()}")
            
            path_bc_sp_outcar = path_bc_sp.joinpath("OUTCAR")

            # Update INCAR file with Bader Charge settings
            ngxf, ngyf, ngzf = outcar_parsers.get_number_grid(path_bc_sp_outcar)
            ngrid = [(3 * int(ngxf)), (3 * int(ngyf)), (3 * int(ngzf))]
            update_incar_bc(path_output_sp.joinpath("INCAR"), f"{mq} [Space Group: {sp}]", ngrid)
            logger.info(f"Updated INCAR for {mq} in space group {sp} with grid dimensions: {ngrid}")

            # Log progress and update system count
            system_count += 1
            progress_bar_show(system_count)
            logger.info(f"Completed input generation for {mq} in space group {sp}. Total systems: {system_count}\n\n")
        

def update_incar_bc(path_incar: Path, system_description: str, number_of_grid: list[int]):
    """
    Updates an INCAR file for Bader charge analysis calculations.

    Args:
        path_incar (Path): Path to the INCAR file
        system_description (str): System description for the SYSTEM tag
        number_of_grid (list[int]): List of grid parameters in the order:
        [NGXF, NGYF, NGZF]
    """
    # Parse the original INCAR file
    dict_flags_incar = incar_parsers.create_incar_dict_flags(path_incar)
    dict_flags_incar['SYSTEM'] = system_description + ' Barder Charge (auto generated INCAR)'
    dict_flags_incar['ISPIN'] = '1'
    dict_flags_incar['NSW'] = '-1'
    dict_flags_incar['IBRION'] = '-1'
    dict_flags_incar['LCHARG'] = '.TRUE.'
    dict_flags_incar['LAECHG'] = '.TRUE.'
    dict_flags_incar['NGXF'] = str(number_of_grid[0])
    dict_flags_incar['NGYF'] = str(number_of_grid[1])
    dict_flags_incar['NGZF'] = str(number_of_grid[2])

    dict_flags_incar.pop('ADDGRID', None)  # Remove ADDGRID if it exists
    dict_flags_incar.pop('EDIFFG', None)  # Remove EDIFFG if it exists
    dict_flags_incar.pop('ISIF', None)  # Remove ISIF if it exists
    dict_flags_incar.pop('POTIM', None)  # Remove POTIM if it exists
    dict_flags_incar.pop('STRESSTYPE', None)  # Remove STRESSTYPE if it exists

    bc_incar_flags = order_dict_by_list(dict_flags_incar, LIST_ORDERED_BC_TAGS)
    # Convert the ordered dictionary back to INCAR format
    bc_incar_flags = incar_parsers.dict_to_pattern_incar(bc_incar_flags)
    with open(path_incar, 'w') as incar_file:
        incar_file.write(bc_incar_flags)



if __name__ == "__main__":
    logger = init_logger(task_name = "BADER_CHARGE", level = "INFO")
else:
    from loguru import logger