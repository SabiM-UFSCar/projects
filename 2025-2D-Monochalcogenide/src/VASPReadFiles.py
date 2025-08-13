import os
import sys

from ase import Atoms
from ase.io.vasp import read_vasp_xml, read_vasp_out
from lxml import etree


class VASPReadFiles:
    """
    A utility class for reading pyVASP simulation files and validating their results.

    This class facilitates the reading and validation of configuration files generated
    by pyVASP (Vienna Ab initio Simulation Package). It provides methods to parse these files,
    validate the simulation results, and generate Atoms objects for further analysis.
    """

    def __init__(self, folder_files):
        """
        Initialize the VASPReadFiles instance.

        :param folder_files: Path to the folder containing pyVASP simulation files.
        """

        if os.path.isdir(folder_files):
            self._path_folder_vasp_files = folder_files
            self._error_simulation_desc = ''
            self._vasprun = None
            self._outcar = None
            self._atoms = None
        else:
            # self._Logger.error('Folder path provided not found. '
            #                    'The specified folder {} does not exist.'.format(folder_files))
            sys.exit(1)

    def _load_data(self):
        """
        Load data from the vasprun.xml file and create the Atoms object.
        """
        _file_name = 'vasprun.xml'
        _path_vasprun = os.path.join(self._path_folder_vasp_files, _file_name)

        # self._Logger.info('Generating the atoms object from the vasprun '
        #                   'file to retrieve the chemical compound descriptors.')
        self._vasprun = read_vasp_xml(_path_vasprun, index=-1)
        for atoms in self._vasprun:
            self._atoms = Atoms(atoms)

    def validate_simulation_results(self):
        """
        Validate the simulation results to ensure successful execution without errors.

        :return: True if the validation is successful, False otherwise.
        """
        # self._Logger.info('Starting the validation process to ensure the simulation has been '
        #                   'successfully executed without errors.')
        _file_name = 'vasprun.xml'
        _path_vasprun = os.path.join(self._path_folder_vasp_files, _file_name)
        try:
            etree.parse(_path_vasprun)
            return True
        except etree.XMLSyntaxError:
            self._error_simulation_desc = self._get_error_simulation()
            return False

    def _get_error_simulation(self):
        """
        Retrieve error details from the simulation output file.

        :return: Description of any errors encountered during the simulation.
        """
        number_line_fatal_error = None
        _lines_error_return = ""
        _file_name = 'saida.out'
        _file_saida_out = os.path.join(self._path_folder_vasp_files, _file_name)
        if os.path.isfile(_file_saida_out):
            try:
                with open(_file_saida_out, 'r') as f:
                    lines_files = f.readlines()

                for i, line in enumerate(lines_files):
                    if ' fatal error ' in line:
                        number_line_fatal_error = i

                if number_line_fatal_error is not None:
                    for number in range(number_line_fatal_error, number_line_fatal_error + 3):
                        if 0 <= number < len(lines_files):
                            _lines_error_return += lines_files[number].strip() + '   '
                return _lines_error_return
            except Exception as e:
                _error_find = f"Error: {e}"
                return _error_find
        else:
            _lines_error_return = f"Specified file:{_file_saida_out} not found!"
            return _lines_error_return

    def read_outcar(self):
        """
        Read data from the OUTCAR file and create the Atoms object.
        """
        _file_name = 'OUTCAR'
        _path_outcar = os.path.join(self._path_folder_vasp_files, _file_name)
        if os.path.isfile(_path_outcar):
            self._outcar = read_vasp_out(_path_outcar, index=-1)
            for atoms in self._outcar:
                self._atoms = Atoms(atoms)
