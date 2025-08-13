import numpy as np

from CORE import CONST as C
from CORE import utils
from VASPDataExtractors.VASPReadFiles import VASPReadFiles


class ResultsExtractor(VASPReadFiles):
    """
    A class for extracting and processing data from pyVASP simulation files.

    This class extends VASPReadFiles to provide methods for extracting data and generating descriptors
    from pyVASP simulation results.

    :param folder_files: The path to the folder containing pyVASP simulation files.
    """

    def __init__(self, folder_files):
        """
        Initialize the ResultsExtractor instance.

        :param folder_files: The path to the folder containing pyVASP simulation files.
        """
        super().__init__(folder_files)
        self._chemical_compounds_path = utils.extract_values_from_string(folder_files, C.LIST_CHEMICAL_COMPOUNDS)
        self._structure_path = utils.extract_values_from_string(folder_files, C.LIST_STRUCTURES)

    def await_validation_simulation_files(self):
        """
        Await validation of simulation files and extract data.

        :return: (dict) Extracted data from the simulation files.
        """
        if self.validate_simulation_results():
            self._load_data()
            return self.extractor_data_from_file()
        else:
            self._load_data()
            error_found = {
                'error': self._error_simulation_desc,
                'path_folder': self._path_folder_vasp_files
            }
            return_data = self.extractor_data_from_file()
            return_data.update(error_found)
            return return_data

    def extractor_data_from_file(self):
        """
        Extract data from the simulation files.

        :return: (dict) Extracted data from the simulation files.
        """
        energy_total_unitary = self._get_energy_total_unitary()
        descriptors_vectors_data = {
            'chemical_compound': self._get_composition(),
            'unitary_chemical_compound': self._unique_elements(),
            'chemical_compound_path': self._chemical_compounds_path,
            'structure_path': self._structure_path,
            'vector_a': self._atoms.cell.cellpar()[0],
            'vector_b': self._atoms.cell.cellpar()[1],
            'vector_c': self._atoms.cell.cellpar()[2],
            'alpha': self._atoms.cell.cellpar()[3],
            'beta': self._atoms.cell.cellpar()[4],
            'gamma': self._atoms.cell.cellpar()[5],
            'layer_thickness': np.max(self._atoms.get_positions()[:, 2]) - np.min(self._atoms.get_positions()[:, 2])
        }
        descriptors_vectors_data.update(energy_total_unitary)
        return descriptors_vectors_data

    def _get_composition(self):
        """
        Calculate the composition of the chemical compound.

        :return: (str) Composition of the chemical compound.
        """
        lst = self._atoms.get_chemical_symbols()
        counts = {}
        for item in lst:
            counts[item] = counts.get(item, 0) + 1

        result = ''.join([f"{key}{value}" for key, value in counts.items()])
        return result

    def _unique_elements(self):
        """
        Get the unique elements in the chemical compound.

        :return: (str) Unique elements in the chemical compound.
        """
        lst = self._atoms.get_chemical_symbols()
        unique_list = []
        seen = set()
        for item in lst:
            if item not in seen:
                unique_list.append(item)
                seen.add(item)
        unique_string = ''.join(unique_list)
        return unique_string

    def _get_energy_total_unitary(self):
        """
        Get the total energy and unitary energy of the system.

        :return: (dict) Total and unitary energy information.
        """
        total_element_numbers = self._return_chemical_symbols_completed()
        total_elements = len(total_element_numbers)

        energy_total_unitary = {
            'e_tot': self._atoms.get_total_energy(),
            'atoms_number': (int(self._atoms.get_global_number_of_atoms()) / int(total_elements)),
            'e_unitary': self._atoms.get_total_energy() / (
                    int(self._atoms.get_global_number_of_atoms()) / int(total_elements))
        }
        return energy_total_unitary

    def _return_chemical_symbols_completed(self):
        """
        Return completed chemical symbols.

        :return: (dict) Completed chemical symbols.
        """
        element_list = self._atoms.get_chemical_symbols()
        element_count = {}
        for element in element_list:
            if element in element_count:
                element_count[element] += 1
            else:
                element_count[element] = 1

        return element_count

    def print_all_information(self):
        """
        Print all available information about the atoms object.
        """
        # Information's
        print("Atomic Numbers:" + str(self._atoms.get_atomic_numbers()))
        print("Initial Charges:" + str(self._atoms.get_initial_charges()))
        print("Chemical Symbols:" + str(self._atoms.get_chemical_symbols()))
        print("Initial Magnetic Moments:" + str(self._atoms.get_initial_magnetic_moments()))
        print("Masses:" + str(self._atoms.get_masses()))
        print("momenta:" + str(self._atoms.get_momenta()))
        print("Forces:" + str(self._atoms.get_forces()))
        print("Positions:" + str(self._atoms.get_positions()))
        print("Scaled Positions (positions relative to unit cell): " + str(self._atoms.get_scaled_positions()))
        print("Tag:" + str(self._atoms.get_tags()))
        print("Velocities:" + str(self._atoms.get_velocities()))
        # Atom
        print("Calculator:" + str(self._atoms.get_calculator()))
        print("Cell:" + str(self._atoms.get_cell()))
        print("Cell Lengths and Angles:" + str(self._atoms.cell.cellpar()))
        print("Center of Mass:" + str(self._atoms.get_center_of_mass()))
        print("Kinetic Energy:" + str(self._atoms.get_kinetic_energy()))
        print("Global number of Atoms:" + str(self._atoms.get_global_number_of_atoms()))
        print("Periodic Boundary Condition:" + str(self._atoms.get_pbc()))
        print("Potential Energy:" + str(self._atoms.get_potential_energy()))
        # print("Stress:" + str(self._atoms.get_stress()))
        print("Total Energy:" + str(self._atoms.get_total_energy()))
        print("Volume:" + str(self._atoms.get_volume()))
        print("All distances: " + str(self._atoms.get_all_distances()))
        print("Angular Momentum: " + str(self._atoms.get_angular_momentum()))
        print("Empirical Formula: " + self._atoms.get_chemical_formula(mode='hill', empirical=True))
        print("Total number of Atoms: " + str(self._atoms.get_global_number_of_atoms()))
        print("Reciprocal Lattice: " + str(self._atoms.cell.reciprocal()))
        print("Number of (non-zero) lattice vectors: " + str(self._atoms.cell.rank))
