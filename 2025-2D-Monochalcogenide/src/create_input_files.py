import mmap
import os
import datetime
import re
import sys
import time
import numpy as np

# This variable stores the absolute path to the directory containing the current script file.
PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
G_POTPAWINFO = []
G_GROUPELEMENTINFO = []


# Function to format the current time in a specific way.
def current_time_to_registrer():
    current_process = datetime.datetime.now()
    formatted_datetime = current_process.strftime("%d_%m_%Y_%H_%M_%S")
    return formatted_datetime


# Function to format the current date in a specific way.
def current_date_to_registrer():
    current_process = datetime.datetime.now()
    formatted_datetime = current_process.strftime("%d_%m_%Y")
    return formatted_datetime


# Function to log information to a specified log file.
def log_registration(PATH_LOG_FILE, TEXT_LOG):
    remove_path_localhost = "/home/user/Simulacao/"
    TEXT_LOG_CHECKED = TEXT_LOG.replace(remove_path_localhost, "")
    with open(PATH_LOG_FILE, 'a') as file:
        file.write("[" + current_time_to_registrer() + "] " + TEXT_LOG_CHECKED + "\n")


def POTCAR_NOT_FOUND(TEXT_LOG):
    PATH_SCRIPT = os.path.dirname(os.path.abspath(__file__))
    PATH_POTCAR_MANUAL = os.path.join(PATH_SCRIPT, "GENERATE_MANUAL_POTCAR")
    with open(PATH_POTCAR_MANUAL, 'a') as file:
        file.write("[" + current_time_to_registrer() + "] " + TEXT_LOG + "\n")


def return_data_formatted_titel(string_data):
    month = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'Mai': 5,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Okt': 10,
        'Nov': 11,
        'Dez': 12
    }
    return_month_abb = r'([A-z]{3})'
    month_abb = re.search(return_month_abb, string_data).group(1)
    int_month = month[month_abb]
    return_day = r'(\d{2})'
    day = re.search(return_day, string_data).group(1)
    return_year = r'(\d{4})'
    year = re.search(return_year, string_data).group(1)

    date_titel = datetime.datetime(int(year), int(int_month), int(day))
    date_return = date_titel.strftime("%d/%m/%Y")
    return date_return


def search_potcar_files(FILE_MAP):
    PATTERN_SEARCH = re.compile(b'TITEL')
    for result in PATTERN_SEARCH.finditer(FILE_MAP):
        start_r = result.start()
        end_r = result.end()

        line_start = FILE_MAP.rfind(b'\n', 0, start_r) + 1
        line_end = FILE_MAP.find(b'\n', end_r)
        string_titel = FILE_MAP[line_start:line_end].decode('utf-8')
        data_file_search = re.compile(r'(\d{1,}[A-z]{3}\d{1,})')
        data_string = re.search(data_file_search, string_titel)
        data_potcat_m = data_string.group(1)
        data_titel_file = return_data_formatted_titel(data_potcat_m)

    PATTERN_SEARCH_ENMAX = re.compile(b'ENMAX')
    for result in PATTERN_SEARCH_ENMAX.finditer(FILE_MAP):
        start_r = result.start()
        end_r = result.end()

        line_start = FILE_MAP.rfind(b'\n', 0, start_r) + 1
        line_end = FILE_MAP.find(b'\n', end_r)
        string_enmax = FILE_MAP[line_start:line_end].decode('utf-8')
        ENMAX_SEARCH_VALUE = r'ENMAX\s*=\s*(\d+.\d+)'
        ENMAX_VALUES = re.search(ENMAX_SEARCH_VALUE, string_enmax)
        if ENMAX_VALUES:
            ENMAX_FLOAT_M = float(ENMAX_VALUES.group(1))

    PATTERN_SEARCH_ZVAL = re.compile(b'ZVAL')
    for result in PATTERN_SEARCH_ZVAL.finditer(FILE_MAP):
        start_r = result.start()
        end_r = result.end()
        line_start = FILE_MAP.rfind(b'\n', 0, start_r) + 1
        line_end = FILE_MAP.find(b'\n', end_r)
        string_zval = FILE_MAP[line_start:line_end].decode('utf-8')
        ZVAL_SEARCH_VALUE = r'ZVAL\s*=\s*(\d+.\d+)'
        ZVAL_VALUES = re.search(ZVAL_SEARCH_VALUE, string_zval)
        if ZVAL_VALUES:
            ZVAL_FLOAT = float(ZVAL_VALUES.group(1))

    return string_titel, data_titel_file, ENMAX_FLOAT_M, ZVAL_FLOAT


def generate_incar(PATH_SCRIPT, PATH_GENERATE, elem_m, elem_q, PATH_LOG_FILE):
    global G_POTPAWINFO
    RATIO_FACTOR = 2.0
    # Path for podpaw folder
    FOLDER_POTPAW_NAME = "potpaw_PBE_5.4_2020_01_15"
    PATH_POTPAW = os.path.join(PATH_SCRIPT, FOLDER_POTPAW_NAME)

    # File Base for INCAR
    INCAR_FILE_NAME = "INCAR_PATTERN"
    INCAR_READ_PATH = os.path.join(PATH_SCRIPT, INCAR_FILE_NAME)

    # Generate Incar file for each chemical composition
    test_file_path = os.path.dirname(os.path.abspath(__file__))
    INCAR_GENERATE_PATH = os.path.join(test_file_path, "INCAR")

    # Path for POTCAR generate
    PATH_POTCAR_GENERATE = os.path.join(test_file_path, "POTCAR")

    log_registration(PATH_LOG_FILE, "            Generate INCAR file for:" + elem_m + elem_q)
    log_registration(PATH_LOG_FILE, "            | -> INCAR PATTERN FILE:" + INCAR_READ_PATH)
    log_registration(PATH_LOG_FILE, "            | -> INCAR PATH:" + INCAR_GENERATE_PATH)

    log_registration(PATH_LOG_FILE, "            | -> Searching for POTCAR files:")
    log_registration(PATH_LOG_FILE, "               | -> Folder name:" + FOLDER_POTPAW_NAME)

    # Search POTCAR file for elements M Q (FIRST -> M, SECOND -> Q)
    POTCAR_LIST_FOLDERS = os.listdir(PATH_POTPAW)

    # Pattern FOLDER name for Element M
    PATTERN_ELEMENT_M = [elem_m + "_GW"]
    if elem_m == "Sn" or elem_m == "In":
        PATTERN_ELEMENT_M = [elem_m + "_d_GW"]

    # Search Element M Folder
    for FOLDERS_NAME in PATTERN_ELEMENT_M:
        if FOLDERS_NAME in POTCAR_LIST_FOLDERS:
            PATH_FOLDER = os.path.join(PATH_POTPAW, FOLDERS_NAME)
            if os.path.exists(PATH_FOLDER) and os.path.isdir(PATH_FOLDER):
                PATH_POTCAR_ELEMENT_M = os.path.join(PATH_FOLDER, "POTCAR")
                log_registration(PATH_LOG_FILE,
                                 "               | -> POTCAR Element " + elem_m + ":" + PATH_POTCAR_ELEMENT_M)
                with open(PATH_POTCAR_ELEMENT_M, 'rb') as POTCAR_M:
                    CONTENT_FILE_M = POTCAR_M.read()
                    FILE_MAP_M = mmap.mmap(POTCAR_M.fileno(), 0, access=mmap.ACCESS_READ)

                log_registration(PATH_LOG_FILE, "               | -> (Element " + elem_m + "):")
                # receive data values from POTCAR
                TITEL_M, DATE_POTCAR_M, ENMAX_M, ZVAL_M = search_potcar_files(FILE_MAP_M)
                log_registration(PATH_LOG_FILE, "                | -> " + TITEL_M)
                log_registration(PATH_LOG_FILE, "                | -> Date:" + DATE_POTCAR_M)
                log_registration(PATH_LOG_FILE, "                | -> ENMAX:" + str(ENMAX_M))
                log_registration(PATH_LOG_FILE, "                | -> ZVAL:" + str(ZVAL_M))
                # Generating datasets for individual elements to construct the information table.
                set_element_m = {'titel': TITEL_M, 'element': elem_m, 'elem_type': 'M', 'data': DATE_POTCAR_M,
                                 'enmax': str(ENMAX_M), 'zval': str(ZVAL_M)}
                G_POTPAWINFO.append(set_element_m)
            break
        else:
            POTCAR_NOT_FOUND("POTCAR: " + FOLDERS_NAME)
            POTCAR_NOT_FOUND("  |---> Elements: " + elem_m + " " + elem_q)

    # Pattern FOLDER name for Element Q
    PATTERN_ELEMENT_Q = [elem_q + "_GW"]

    for FOLDERS_NAME in PATTERN_ELEMENT_Q:
        if FOLDERS_NAME in POTCAR_LIST_FOLDERS:
            PATH_FOLDER = os.path.join(PATH_POTPAW, FOLDERS_NAME)
            if os.path.exists(PATH_FOLDER) and os.path.isdir(PATH_FOLDER):
                PATH_POTCAR_ELEMENT_Q = os.path.join(PATH_FOLDER, "POTCAR")
                log_registration(PATH_LOG_FILE,
                                 "               | -> POTCAR Element " + elem_q + ":" + PATH_POTCAR_ELEMENT_Q)
                with open(PATH_POTCAR_ELEMENT_Q, 'rb') as POTCAR_Q:
                    CONTENT_FILE_Q = POTCAR_Q.read()
                    FILE_MAP_Q = mmap.mmap(POTCAR_Q.fileno(), 0, access=mmap.ACCESS_READ)

                log_registration(PATH_LOG_FILE, "               | -> (Element " + elem_q + "):")
                # receive data values from POTCAR
                TITEL_Q, DATE_POTCAR_Q, ENMAX_Q, ZVAL_Q = search_potcar_files(FILE_MAP_Q)
                log_registration(PATH_LOG_FILE, "                | -> " + TITEL_Q)
                log_registration(PATH_LOG_FILE, "                | -> Date:" + DATE_POTCAR_Q)
                log_registration(PATH_LOG_FILE, "                | -> ENMAX:" + str(ENMAX_Q))
                log_registration(PATH_LOG_FILE, "                | -> ZVAL:" + str(ZVAL_Q))
                # Generating datasets for individual elements to construct the information table.
                set_element_q = {'titel': TITEL_Q, 'element': elem_q, 'elem_type': 'Q', 'data': DATE_POTCAR_Q,
                                 'enmax': str(ENMAX_Q), 'zval': str(ZVAL_Q)}
                G_POTPAWINFO.append(set_element_q)
            break
        else:
            POTCAR_NOT_FOUND("POTCAR: " + FOLDERS_NAME)
            POTCAR_NOT_FOUND("  |---> Elements: " + elem_m + " " + elem_q)

    # Determine which one has the highest maximum energy
    if ENMAX_M > ENMAX_Q:
        INCAR_ENCUT = ENMAX_M * RATIO_FACTOR
        log_registration(PATH_LOG_FILE, "                | -> ENMAX used:" + elem_m)
    elif ENMAX_Q > ENMAX_M:
        INCAR_ENCUT = ENMAX_Q * RATIO_FACTOR
        log_registration(PATH_LOG_FILE, "                | -> ENMAX used:" + elem_q)
    else:
        INCAR_ENCUT = ENMAX_Q * RATIO_FACTOR
        log_registration(PATH_LOG_FILE, "                | -> ENMAX used:" + elem_q)

    log_registration(PATH_LOG_FILE, "                  | -> RATIO_FACTOR used:" + str(RATIO_FACTOR))
    log_registration(PATH_LOG_FILE, "                  | -> ENCUT for INCAR:" + str(INCAR_ENCUT))
    set_incar_info = {
        'incar_encut': str(INCAR_ENCUT),
        'incar_ratio_factor': str(RATIO_FACTOR),
    }

    # Reading the STANDARD INCAR FILE
    with open(INCAR_READ_PATH, 'r') as INCAR_READ:
        lines_incar = INCAR_READ.readlines()

    with open(INCAR_GENERATE_PATH, 'a') as INCAR_GENERATE:
        for line_number, lines in enumerate(lines_incar, start=1):
            if line_number == 1:
                new_line = "#SYSTEM " + elem_m + " " + elem_q + " - (auto generated INCAR)\n"
                INCAR_GENERATE.writelines(new_line)
            elif line_number == 4:
                new_line = "ENCUT   =   " + str(INCAR_ENCUT) + "\n"
                INCAR_GENERATE.writelines(new_line)
            else:
                INCAR_GENERATE.writelines(lines)
    log_registration(PATH_LOG_FILE, "             INCAR files generated successfully")

    # CREATE POTCAR FILE FOR ELEMENTS FIRST ELEMENT M , SECOND ELEMENT Q
    CONTENT_FILE_Q_M = CONTENT_FILE_M + CONTENT_FILE_Q
    log_registration(PATH_LOG_FILE, "             POTCAR file generated")
    log_registration(PATH_LOG_FILE, "               | -> FIRST POTCAR:" + TITEL_M)
    log_registration(PATH_LOG_FILE, "               | -> SECOND POTCAR:" + TITEL_Q)
    with open(PATH_POTCAR_GENERATE, 'wb') as POTCAR_Q_M:
        POTCAR_Q_M.write(CONTENT_FILE_Q_M)

    log_registration(PATH_LOG_FILE, "               | -> PATH POTCAR:" + PATH_POTCAR_GENERATE)
    log_registration(PATH_LOG_FILE, "             POTCAR files generated successfully")
    return set_incar_info


def generate_poscar(PATH_SPACE_GROUP, PATH_GENERATE, elem_m, elem_q, PATH_LOG_FILE):
    POSCAR_FILE_NAME = "POSCAR_VACCUM_AUTO"
    test_file_path = os.path.dirname(os.path.abspath(__file__))
    POSCAR_GENERATE_PATH = os.path.join(test_file_path, "POSCAR")
    POSCAR_READ_PATH = os.path.join(PATH_SPACE_GROUP, POSCAR_FILE_NAME)
    log_registration(PATH_LOG_FILE, "            Generate POSCAR file for:" + elem_m + elem_q)
    log_registration(PATH_LOG_FILE, "            | -> POSCAR PATTERN FILE:" + POSCAR_READ_PATH)
    log_registration(PATH_LOG_FILE, "            | -> POSCAR PATH:" + POSCAR_GENERATE_PATH)

    # Leitura do ARQUIVO POSCAR PADRAO
    with open(POSCAR_READ_PATH, 'r') as POSCAR_READ:
        lines_poscar = POSCAR_READ.readlines()

    list_lines_change = [1, 6]
    pattern_numbers_retrive = re.compile(r"(\d+)")

    with open(POSCAR_GENERATE_PATH, 'a') as POSCAR_GENERATE:
        for line_number, lines in enumerate(lines_poscar, start=1):
            if line_number in list_lines_change:
                if line_number == 1:
                    numbers = pattern_numbers_retrive.findall(lines)
                    new_line = elem_m + str(numbers[0]) + " " + elem_q + str(
                        numbers[1]) + " - (auto generated POSCAR)\n"
                    POSCAR_GENERATE.writelines(new_line)
                if line_number == 6:
                    new_line = elem_m + "   " + elem_q + "\n"
                    POSCAR_GENERATE.writelines(new_line)
            else:
                POSCAR_GENERATE.writelines(lines)
        log_registration(PATH_LOG_FILE,
                         "            | -> Chemistry formula M:" + elem_m + str(numbers[0]) + " Q: " + elem_q + str(
                             numbers[1]))
    log_registration(PATH_LOG_FILE, "            POSCAR files generated successfully")


def creat_input_files(PATH_ROOT):
    global G_GROUPELEMENTINFO
    PATH_LOG_FILE = os.path.join(PATH_ROOT, "log_input_file_" + current_date_to_registrer())
    log_registration(PATH_LOG_FILE, "Scanning Subfolders:")

    LIST_CRYSTAL_SYSTEM = [list_files for list_files in os.listdir(PATH_ROOT) if
                           os.path.isdir(os.path.join(PATH_ROOT, list_files))]

    FOLDER_POTPAW = "potpaw_PBE_5.4_2020_01_15"
    LIST_CRYSTAL_SYSTEM = [item for item in LIST_CRYSTAL_SYSTEM if item != FOLDER_POTPAW]

    for CRYSTAL_SYSTEM in LIST_CRYSTAL_SYSTEM:
        log_registration(PATH_LOG_FILE, CRYSTAL_SYSTEM)
        PATH_SPACE_GROUP = os.path.join(PATH_ROOT, CRYSTAL_SYSTEM)
        LIST_SPACE_GROUP = [list_group for list_group in os.listdir(PATH_SPACE_GROUP) if
                            os.path.isdir(os.path.join(PATH_SPACE_GROUP, list_group))]
        for SPACE_GROUP in LIST_SPACE_GROUP:
            log_registration(PATH_LOG_FILE, " |----> " + SPACE_GROUP)
            PATH_SPACE_GROUP_FOLDER = os.path.join(PATH_SPACE_GROUP, SPACE_GROUP)

            LIST_PERIODIC_TABLE_GROUP = [list_table_group for list_table_group in os.listdir(PATH_SPACE_GROUP_FOLDER) if
                                         os.path.isdir(os.path.join(PATH_SPACE_GROUP_FOLDER, list_table_group))]

            for TABLE_GROUP in LIST_PERIODIC_TABLE_GROUP:
                log_registration(PATH_LOG_FILE, "   |----> " + TABLE_GROUP)
                PATH_TABLE_GROUP_FOLDER = os.path.join(PATH_SPACE_GROUP_FOLDER, TABLE_GROUP)
                LIST_CHEMICAL_COMPOSITION = [list_composition for list_composition in
                                             os.listdir(PATH_TABLE_GROUP_FOLDER) if
                                             os.path.isdir(os.path.join(PATH_TABLE_GROUP_FOLDER, list_composition))]

                for CH_COMPOSITON in LIST_CHEMICAL_COMPOSITION:
                    PATH_CH_COMPOSITION = os.path.join(PATH_TABLE_GROUP_FOLDER, CH_COMPOSITON)
                    # Pattern for disassembling the chemical structure
                    pattern_ch_composition = re.compile(r"([A-Z][a-z]*)")
                    composition_list = pattern_ch_composition.findall(CH_COMPOSITON)
                    log_registration(PATH_LOG_FILE, "       |----> " + CH_COMPOSITON)
                    element_M = composition_list[0]
                    element_Q = composition_list[1]
                    log_registration(PATH_LOG_FILE, "            M = " + element_M + " Q = " + element_Q)
                    # Call the function to create the POSCAR file.
                    generate_poscar(PATH_SPACE_GROUP_FOLDER, PATH_CH_COMPOSITION, element_M, element_Q, PATH_LOG_FILE)
                    # Call the function to create the INCAR file.
                    rt_info = generate_incar(PATH_ROOT, PATH_CH_COMPOSITION, element_M, element_Q, PATH_LOG_FILE)
                    # Preparing data for each chemical formula to compile the information table.
                    set_grp_info = {
                        'crystal_system': CRYSTAL_SYSTEM,
                        'space_group': SPACE_GROUP,
                        'table_group': TABLE_GROUP,
                        'ch_compositon': CH_COMPOSITON,
                        'element_m': element_M,
                        'element_q': element_Q,
                        'incar_info': rt_info
                    }
                    G_GROUPELEMENTINFO.append(set_grp_info)


def remove_duplicate_potpawinfo():
    global G_POTPAWINFO
    list_unique = []
    key_set = set()
    for element_podpaw in G_POTPAWINFO:
        podpaw_sorted = tuple(sorted(element_podpaw.items()))
        if podpaw_sorted not in key_set:
            list_unique.append(element_podpaw)
            key_set.add(podpaw_sorted)

    array_return = sorted(list_unique, key=atomic_number_element)
    for elements in array_return:
        elements['atomic_number'] = atomic_number_element(elements)
    return array_return


def tableLatex_potcar():
    potcar_list = remove_duplicate_potpawinfo()
    global PATH_ROOT
    PATH_LATEX_TABLE_POTCAR = os.path.join(PATH_ROOT, "GENERATE_LATEX_POTCAR_INFO")
    with open(PATH_LATEX_TABLE_POTCAR, 'a') as file:
        file.write("\\begin{table}[h]")
        file.write('\n')
        file.write("\caption{POTCAR File Information}")
        file.write('\n')
        file.write("\label{tab:potcar_information}")
        file.write('\n')
        file.write("\\resizebox{\\textwidth}{!}{\\begin{tabular}{|l|l|l|l|l|l|l|l|}")
        file.write('\n')
        file.write("\hline")
        file.write('\n')
        file.write(
            "Titel & Element & Element type & Date POTCAR & ENMAX (eV) & Nº valence electrons  \\\\ \hline")
        file.write('\n')
        for set_element in potcar_list:
            file.write(
                f'{formatted_titel(set_element["titel"])} & {set_element["element"]}  & {set_element["elem_type"]}  & {set_element["data"]} & $ {number_formatted_float(set_element["enmax"])} $ & $ {number_formatted_int(set_element["zval"])} $ \\\\ \hline')
            file.write('\n')

        # Close table
        file.write("\end{tabular}}")
        file.write('\n')
        file.write("\end{table}")


def formatted_titel(titel_str):
    titel = titel_str.split()
    titel_return = ' '.join(titel[1:-1])
    titel_return = titel_return.replace("_", "\_")
    titel_return = titel_return.replace("=", "")

    return titel_return.strip()


# Generate LaTeX tables for information on each space group
def tableLatex_spacegroup():
    global G_GROUPELEMENTINFO
    global PATH_ROOT
    PATH_LATEX_TABLE_SG = os.path.join(PATH_ROOT, "GENERATE_LATEX_SPACE_GROUP")
    with open(PATH_LATEX_TABLE_SG, 'a') as file:
        file.write("\\begin{table}[]")
        file.write('\n')
        file.write("\caption{Information on each space group.}")
        file.write('\n')
        file.write("\label{tab:space_group_information}")
        file.write('\n')
        file.write("\\resizebox{\\textwidth}{!}{\\begin{tabular}{|l|l|l|l|l|l|l|l|}")
        file.write('\n')
        file.write("\hline")
        file.write('\n')
        file.write(
            "Crystal System & Space Group & Periodic Table Group & Chemical Composition & Ratio Factor INCAR & ENCUT (eV) \\\\ \hline")
        file.write('\n')
        for set_element in G_GROUPELEMENTINFO:
            file.write(
                f'{crystal_correction(set_element["crystal_system"])} & {structure_correction(set_element["space_group"])}  & {set_element["table_group"]}  & {set_element["ch_compositon"]} & $ {number_formatted_int(set_element["incar_info"]["incar_ratio_factor"])} $ & $ {number_formatted_float(set_element["incar_info"]["incar_encut"])} $ \\\\ \hline')
            file.write('\n')

        # Close table
        file.write("\end{tabular}}")
        file.write('\n')
        file.write("\end{table}")


def crystal_correction(crystal):
    if crystal == "OrthorombicStructures":
        crystal_return = "Orthorombic"
    elif crystal == "HexagonalStructures":
        crystal_return = "Hexagonal"
    elif crystal == "TriclinicStructures":
        crystal_return = "Triclinic"
    else:
        crystal_return = crystal

    return crystal_return


def structure_correction(structure):
    if structure == "P3m1_alpha":
        structure_return = "\\texorpdfstring{P$\\bar{3}$m1 $\\alpha$}{P3m1 alpha}"
    elif structure == "P3m1_beta":
        structure_return = "\\texorpdfstring{P$\\bar{3}$m1 $\\beta$}{P3m1 beta}"
    elif structure == "P6m2":
        structure_return = "\\texorpdfstring{P$\\bar{6}$m2}{P6m2}"
    elif structure == "C2_m":
        structure_return = "C2/m"
    elif structure == "P2_1c":
        structure_return = "\\texorpdfstring{$P2_1 / c$}{P21 / c}"
    elif structure == "P4_nmm":
        structure_return = "P4/nmm"
    elif structure == "P_1_alpha":
        structure_return = "\\texorpdfstring{P$\\bar{1}$ $\\alpha$}{P-1 alpha}"
    elif structure == "P_1_beta":
        structure_return = "\\texorpdfstring{P$\\bar{1}$ $\\beta$}{P-1 beta}"
    elif structure == "Ph_like":
        structure_return = "\\texorpdfstring{$Pmn2_{1}$ (Ph-Like)}{Pmn2_1 (Ph-Like)}"
    else:
        structure_return = structure

    return structure_return


def number_formatted_float(str_number):
    try:
        number = float(str_number)
        number_return = format(number, '.3f')
        return str(number_return)
    except ValueError:
        return str_number


def number_formatted_int(str_number):
    try:
        number = float(str_number)
        number_return = int(number)
        return str(number_return)
    except ValueError:
        return str_number


def atomic_number_element(find):
    element = {
        "H": 1,
        "He": 2,
        "Li": 3,
        "Be": 4,
        "B": 5,
        "C": 6,
        "N": 7,
        "O": 8,
        "F": 9,
        "Ne": 10,
        "Na": 11,
        "Mg": 12,
        "Al": 13,
        "Si": 14,
        "P": 15,
        "S": 16,
        "Cl": 17,
        "Ar": 18,
        "K": 19,
        "Ca": 20,
        "Sc": 21,
        "Ti": 22,
        "V": 23,
        "Cr": 24,
        "Mn": 25,
        "Fe": 26,
        "Co": 27,
        "Ni": 28,
        "Cu": 29,
        "Zn": 30,
        "Ga": 31,
        "Ge": 32,
        "As": 33,
        "Se": 34,
        "Br": 35,
        "Kr": 36,
        "Rb": 37,
        "Sr": 38,
        "Y": 39,
        "Zr": 40,
        "Nb": 41,
        "Mo": 42,
        "Tc": 43,
        "Ru": 44,
        "Rh": 45,
        "Pd": 46,
        "Ag": 47,
        "Cd": 48,
        "In": 49,
        "Sn": 50,
        "Sb": 51,
        "Te": 52,
        "I": 53,
        "Xe": 54,
        "Cs": 55,
        "Ba": 56,
        "La": 57,
        "Ce": 58,
        "Pr": 59,
        "Nd": 60,
        "Pm": 61,
        "Sm": 62,
        "Eu": 63,
        "Gd": 64,
        "Tb": 65,
        "Dy": 66,
        "Ho": 67,
        "Er": 68,
        "Tm": 69,
        "Yb": 70,
        "Lu": 71,
        "Hf": 72,
        "Ta": 73,
        "W": 74,
        "Re": 75,
        "Os": 76,
        "Ir": 77,
        "Pt": 78,
        "Au": 79,
        "Hg": 80,
        "Tl": 81,
        "Pb": 82,
        "Bi": 83,
        "Po": 84,
        "At": 85,
        "Rn": 86,
        "Fr": 87,
        "Ra": 88,
        "Ac": 89,
        "Th": 90,
        "Pa": 91,
        "U": 92,
        "Np": 93,
        "Pu": 94,
        "Am": 95,
        "Cm": 96,
        "Bk": 97,
        "Cf": 98,
        "Es": 99,
        "Fm": 100,
        "Md": 101,
        "No": 102,
        "Lr": 103,
        "Rf": 104,
        "Db": 105,
        "Sg": 106,
        "Bh": 107,
        "Hs": 108,
        "Mt": 109,
    }

    if find['element'] in element:
        return element[find['element']]
    else:
        return 0


def generate_kpoints(PATH_POSCAR, rK_fator,PATH_LOG_FILE):
    # File Base for KPOINTS rK CALC
    POSCAR_FILE_NAME = "POSCAR_VACCUM_AUTO"
    POSCAR_READ_PATH = os.path.join(PATH_POSCAR, POSCAR_FILE_NAME)


    # Generate K-points file for each chemical composition
    # Regular k-point mesh
    # 0              ! 0 -> determine number of k points automatically
    # Gamma          ! generate a Gamma centered mesh
    # 7 7 1          !subdivisions N_1, N_2 and N_3 along the reciprocal lattice vectors (Rk = 30)
    # 0  0  0        ! optional shift of the mesh (s_1, s_2, s_3)
    file_path = os.path.dirname(os.path.abspath(__file__))
    KPOINTS_GENERATE_PATH = os.path.join(file_path, "KPOINTS")

    log_registration(PATH_LOG_FILE, "            Generate KPOINTS file for:")
    log_registration(PATH_LOG_FILE, "            | -> KPOINTS rK factor:" + str(rK_fator))
    log_registration(PATH_LOG_FILE, "            | -> KPOINTS PATH:" + KPOINTS_GENERATE_PATH)
    log_registration(PATH_LOG_FILE,
                     "            | -> calculating the values of N_1, N_2 and N_3 along the reciprocal lattice vectors")
    with open(POSCAR_READ_PATH, 'r') as POSCAR_READ:
        cFlag = POSCAR_READ.readline()
        ifactor = POSCAR_READ.readline()
        str_vec1 = POSCAR_READ.readline()
        str_vec2 = POSCAR_READ.readline()
        str_vec3 = POSCAR_READ.readline()


def rkmesh2D(rk, rlat, ifactor):
    ngrid = np.zeros(3, dtype=np.int64)
    blat = np.zeros((3, 3), dtype=np.float64)
    vsize = np.zeros(3, dtype=np.float64)
    pi = np.arccos(-1.0)

    # Factor correction:
    for vec in rlat:
        vec *= ifactor

    blat = recvec(rlat[0], rlat[1], rlat[2])

    for i in range(3):
        vsize[i] = vecsize(blat[i])

    vsize = vsize / (2.0 * pi)

    ngrid[0] = int(max(1.0, (rk * vsize[0]) + 0.5))
    ngrid[1] = int(max(1.0, (rk * vsize[1]) + 0.5))
    ngrid[2] = 1

    return ngrid

# Calculates the vector resulting from the cross product of two vectors v1 × v2
def prodvec(v1, v2):
    vx = np.zeros(3, dtype=np.float64)
    vx[0] = (v1[1] * v2[2]) - (v1[2] * v2[1])
    vx[1] = (v1[2] * v2[0]) - (v1[0] * v2[2])
    vx[2] = (v1[0] * v2[1]) - (v1[1] * v2[0])
    return vx


def recvec(rlat1, rlat2, rlat3):
    pi = np.pi

    v23 = np.empty(3, dtype=np.float64)
    v31 = np.empty(3, dtype=np.float64)
    v12 = np.empty(3, dtype=np.float64)

    blat1 = np.empty(3, dtype=np.float64)
    blat2 = np.empty(3, dtype=np.float64)
    blat3 = np.empty(3, dtype=np.float64)

    v23 = prodvec(rlat2, rlat3)
    v31 = prodvec(rlat3, rlat1)
    v12 = prodvec(rlat1, rlat2)

    vol = abs((rlat1[0] * v23[0]) + (rlat1[1] * v23[1]) + (rlat1[2] * v23[2]))

    blat1 = ((2.0 * pi) / vol) * v23
    blat2 = ((2.0 * pi) / vol) * v31
    blat3 = ((2.0 * pi) / vol) * v12

    return blat1, blat2, blat3


def vecsize(vec):
    vsize = np.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
    return vsize

