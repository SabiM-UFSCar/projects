import datetime
import os
import re
import shutil
from ase.io.vasp import read_vasp_out
from ase import Atoms
from CORE import CONST as C
from ReportGeneration import JsonBuilder
from VASPStructuresFile import KPOINTSCalculator
from ReportGeneration import LatexWriter


def log_register(string):
    date_time_now = datetime.datetime.now()
    date_time_formatted = date_time_now.strftime("[%Y-%m-%d %H:%M:%S]")
    path_log_file = os.path.join(C.PATH_FOLDER_LOG, 'simulation_dos_generation.log')
    with open(path_log_file, 'a') as log:
        log.write(date_time_formatted + ' ' + string + '\n')


def create_structure_folders():
    path_output = os.path.join(C.PATH_FOLDER_SIMULATION_FILES, 'simulation_dos')
    chemical_compounds_structures = [
        ['AlS', 'P6m2'], ['AlSe', 'P6m2'], ['AlTe', 'P_1_beta'],
        ['GaS', 'P6m2'], ['GaSe', 'P6m2'], ['GaTe', 'P_1_beta'],
        ['InS', 'P6m2'], ['InSe', 'P6m2'], ['InTe', 'P6m2'],
        ['SiS', 'Pmna'], ['SiSe', 'Pmna'], ['SiTe', 'Pmna'],
        ['GeS', 'P3m1_alpha'], ['GeSe', 'P3m1_alpha'], ['GeTe', 'P3m1_alpha'],
        ['SnS', 'Ph_like'], ['SnSe', 'Ph_like'], ['SnTe', 'P3m1_alpha'],
        ['PS', 'P2_1c'], ['PSe', 'P2_1c'], ['PTe', 'P2_1c'],
        ['AsS', 'P2_1c'], ['AsSe', 'P2_1c'], ['AsTe', 'P2_1c'],
        ['SbS', 'P2_1c'], ['SbSe', 'P2_1c'], ['SbTe', 'P_1_beta']
    ]

    list_files_input = ['INCAR', 'POSCAR', 'POTCAR', 'KPOINTS', 'OUTCAR']
    information = []

    for dos_sim in chemical_compounds_structures:
        log_register(f'DOS Simulations: {dos_sim[0]} - {dos_sim[1]}')

        log_register(f'   - Created folder structure: {dos_sim[0]}/{dos_sim[1]}')
        _path_folder_structure = os.path.join(path_output, dos_sim[0] + '/' + dos_sim[1])
        os.makedirs(_path_folder_structure, exist_ok=True)
        log_register(f'   - Copy files:')
        for file in list_files_input:
            path_input = os.path.join(C.PATH_FOLDER_STATIC_TOTAL_ENERGY, dos_sim[0] + '/' + dos_sim[1])
            path_file_input = os.path.join(path_input, file)
            path_file_output = os.path.join(_path_folder_structure, file)
            shutil.copy2(path_file_input, path_file_output)
            log_register(f'          | - File: {file} ')
            log_register(f'               - Reference folder: {path_file_input} ')

        log_register(f'   - Setting up files for DOS simulation')
        log_register(f'      - KPOINTS:')
        ngrid = kpoints_read(_path_folder_structure)
        ngridx2 = [
            2 * int(ngrid[0]),
            2 * int(ngrid[1]),
            int(ngrid[2])
        ]
        ngrid_calc = kpoints_calc(_path_folder_structure)
        create_kpoints(_path_folder_structure, ngrid_calc)
        log_register(f'         - CURRENT NGRID:{ngrid[0]}, {ngrid[1]}, {ngrid[2]}')
        log_register(f'         - 2 TIMES NGRID:{ngridx2[0]}, {ngridx2[1]}, {ngridx2[2]}')
        log_register(f'         - NGRID CALCULATED FOR RK=60:{ngrid_calc[0]}, {ngrid_calc[1]}, {ngrid_calc[2]}')
        log_register(f'      - INCAR:')
        nbands, ispin = incar_read(_path_folder_structure)
        _compounds = {
            'Compounds': dos_sim[0],
            'S.G': LatexWriter.latex_valid_name_for_point_group(dos_sim[1]),
            'NGrid': f'{ngrid_calc[0]},{ngrid_calc[1]},{ngrid_calc[2]}',
            'ISPIN': ispin,
            'NBANDS': nbands
        }
        information.append(_compounds)
        # remove OUTCAR
        path_outcar = os.path.join(_path_folder_structure, 'OUTCAR')
        if os.path.exists(path_outcar):
            os.remove(path_outcar)
    _path_json = os.path.join(C.PATH_FOLDER_JSON_FILES, 'json_dos_simulation.json')
    JsonBuilder.generate_json_from_list_dicts(information, _path_json)


def incar_read(path_files):
    _path_outcar = os.path.join(path_files, 'OUTCAR')
    outcar_obj = Atoms(read_vasp_out(_path_outcar))
    magmoment = abs(outcar_obj.get_magnetic_moment())
    if magmoment < 0.1:
        ispin = 1
    else:
        ispin = 2
    _file = 'INCAR'
    _file_path = os.path.join(path_files, _file)
    _match_ispin = r'ISPIN\s*='
    _line_ispin = f'ISPIN = {ispin}\n'
    _match_sigma = r'SIGMA\s*='
    _line_sigma = 'SIGMA = 0.01\n'
    _match_lorbit = r'LORBIT\s*='
    _line_pos_lorbit = 'NEDOS = 6001\n'
    nelect = outcar_read(path_files)
    _line_pos_nedos = f'NBANDS = {nelect}\n'  # NELECT - OUTCAR
    _match_lcharg = r'LCHARG\s*='
    _line_lcharg = 'LCHARG = .TRUE.\n'
    incar_content = ''

    with open(_file_path, 'r') as incar_file:
        lines = incar_file.readlines()

    for line_number, content in enumerate(lines, start=1):
        if re.search(_match_ispin, content):
            incar_content += _line_ispin
        elif re.search(_match_sigma, content):
            incar_content += _line_sigma
        elif re.search(_match_lorbit, content):
            incar_content += content
            incar_content += _line_pos_lorbit
            incar_content += _line_pos_nedos
        elif re.search(_match_lcharg, content):
            incar_content += _line_lcharg
        else:
            incar_content += content

    create_incar(path_files, incar_content)
    return nelect, ispin


def create_incar(path_files, content):
    _file = 'INCAR'
    _file_path = os.path.join(path_files, _file)
    with open(_file_path, 'w') as incar:
        incar.write(content)


def outcar_read(path_files):
    _file = 'OUTCAR'
    _file_path = os.path.join(path_files, _file)
    _match_nelect = r'NELECT\s*='
    nelect_return = 0
    with open(_file_path, 'r') as outcar_file:
        lines = outcar_file.readlines()

    for line_number, content in enumerate(lines, start=1):
        if re.search(_match_nelect, content):
            list_content = content.strip().split()
            nelect = list_content[2]
            nelect_return = int(float(nelect))

    return nelect_return


def create_kpoints(path_files, ngrid):
    _path_kpoints_generate = os.path.join(path_files, 'KPOINTS')
    with open(_path_kpoints_generate, 'w') as kpoints_file:
        kpoints_file.writelines("Regular k-point mesh (auto generated KPOINTS)\n")
        kpoints_file.writelines("0\n")
        kpoints_file.writelines("Gamma\n")
        kpoints_file.writelines(f"{str(ngrid[0])} {str(ngrid[1])} {str(ngrid[2])}\n")
        kpoints_file.writelines("0 0 0\n")


def kpoints_calc(path_files):
    path_poscar = os.path.join(path_files, 'POSCAR')
    if os.path.exists(path_poscar):
        with open(path_poscar, 'r') as poscar_read:
            poscar_read.readline().strip()
            ifactor = int(float(poscar_read.readline().strip()))
            str_vec1 = poscar_read.readline().strip()
            str_vec2 = poscar_read.readline().strip()
            str_vec3 = poscar_read.readline().strip()

        a_vec = str_vec1.split()
        b_vec = str_vec2.split()
        c_vec = str_vec3.split()

        lattice_vectors = [
            [float(a_vec[0]), float(a_vec[1]), float(a_vec[2])],
            [float(b_vec[0]), float(b_vec[1]), float(b_vec[2])],
            [float(c_vec[0]), float(c_vec[1]), float(c_vec[2])]
        ]

        ngrid = KPOINTSCalculator.rkmesh2d(60, lattice_vectors, ifactor)
        return ngrid


def kpoints_read(path_files):
    _file = 'KPOINTS'
    _file_path = os.path.join(path_files, _file)
    with open(_file_path, 'r') as kpoints_file:
        lines = kpoints_file.readlines()
        for line, contend in enumerate(lines, start=1):
            if line == 4:
                ngrid = contend.strip().split()

    return ngrid
