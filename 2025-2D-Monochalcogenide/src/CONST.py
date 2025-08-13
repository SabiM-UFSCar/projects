import os

RKFACTOR = 30

_BASE_DIR_SCRIPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_PATH = '/home/user/simulation'

# The list containing all 27 selected chemical components for the simulation.
LIST_CHEMICAL_COMPOUNDS = ['AlS', 'AlSe', 'AlTe', 'GaS', 'GaSe', 'GaTe', 'InS', 'InSe', 'InTe', 'SiS', 'SiSe', 'SiTe',
                           'GeS', 'GeSe', 'GeTe', 'SnS', 'SnSe', 'SnTe', 'PS', 'PSe', 'PTe', 'AsS', 'AsSe', 'AsTe',
                           'SbS', 'SbSe', 'SbTe']

# The list comprising all 13 selected crystal structures for the simulation.
'''
The Ph_like structure is also referenced as Pmn21 in the literature. 
Although we initially used the Ph_like nomenclature, we maintain this naming convention in the script for 
generating the files.
'''
LIST_STRUCTURES = ['Aem2', 'C2_m', 'P_1_alpha', 'P_1_beta', 'P2_1c', 'P3m1_alpha', 'P3m1_beta', 'P4_nmm',
                   'P6m2', 'Pbcm', 'Ph_like', 'Pmmn', 'Pmna']

PATH_FOLDER_POTPAW = os.path.join(_BASE_DIR_SCRIPT, 'data/potpaw_PBE_5_4_2020_01_15')
PATH_FOLDER_POSCAR_PATTERN = os.path.join(_BASE_DIR_SCRIPT, 'data/poscar_pattern')
PATH_FOLDER_INCAR_PATTERN = os.path.join(_BASE_DIR_SCRIPT, 'data/incar_pattern')

PATH_FOLDER_SIMULATION_FILES = os.path.join(_BASE_DIR_SCRIPT, 'OUTPUT/SimulationFiles')
PATH_FOLDER_LOG = os.path.join(_BASE_DIR_SCRIPT, 'OUTPUT/log')
PATH_FOLDER_REPORTS = os.path.join(_BASE_DIR_SCRIPT, 'OUTPUT/reports')
PATH_FOLDER_JSON_FILES = os.path.join(PATH_FOLDER_REPORTS, 'json')
PATH_FOLDER_LATEX_FILES = os.path.join(PATH_FOLDER_REPORTS, 'latex')
PATH_FOLDER_TXT_FILES = os.path.join(PATH_FOLDER_REPORTS, 'txt')
PATH_FOLDER_RESULTS_SIMULATIONS = os.path.join(BASE_PATH, 'IC/FinalSimulationFiles')
PATH_FOLDER_STATIC_TOTAL_ENERGY = os.path.join(PATH_FOLDER_RESULTS_SIMULATIONS, 'StaticCalculationTotalEnergy')
PATH_FOLDER_STRESS_RELAXATION = os.path.join(PATH_FOLDER_RESULTS_SIMULATIONS, 'StressRelaxation')
