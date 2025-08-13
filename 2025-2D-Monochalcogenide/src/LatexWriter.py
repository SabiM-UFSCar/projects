import json
import os
import sys


def format_latex_text(text):
    """
    Format text for LaTeX compatibility by replacing underscores with escaped underscores.

    :param text: The input text to be formatted.
    :return: Formatted text compatible with LaTeX.
    """
    return text.replace('_', '\\_')


def latex_valid_name_for_point_group(point_group_name):
    """
    Returns the valid LaTeX representation of a crystallographic point group name.

    :param point_group_name: The name of the crystallographic point group.

    :return: str or None: The valid LaTeX representation of the point group name, or None if not found.

    Example Usage:
        latex_valid_name_for_point_group('P3m1_alpha')
        'P$\\bar{3}$m1 $\\alpha$'

    Note:
        This function maps crystallographic point group names to their valid LaTeX representations.
        If the point group name is not found in the mapping, it returns None.

    """
    point_group_base_name = {
        'P3m1_alpha': 'P$\\bar{3}$m1 $\\alpha$',
        'P6m2': 'P$\\bar{6}$m2',
        'Aem2': 'Aem2',
        'P3m1_beta': 'P$\\bar{3}$m1 $\\beta$',
        'Pmna': 'Pmna',
        'C2_m': 'C2/m',
        'P2_1c': '$P2_1/c$',
        'P4_nmm': 'P4/nmm',
        'P_1_alpha': 'P$\\bar{1}$ $\\alpha$',
        'P_1_beta': 'P$\\bar{1}$ $\\beta$',
        'Pbcm': 'Pbcm',
        'Pmmn': 'Pmmn',
        'Ph_like': '$Pmn2_{1}$'

    }

    return point_group_base_name.get(point_group_name, None)


def generate_latex_table_info_relaxation_results(file_json, file_output):
    """
    Generates a LaTeX table with relaxation results from a JSON file.

    :param file_json: The path to the input JSON file containing relaxation results.
    :param file_output: The path to the output LaTeX file to be generated.

    :return: None

    Reads data from the specified JSON file and creates a LaTeX table containing
    information about relaxation results. The table includes chemical formulas,
    structural information, lattice parameters, and energy values. The generated
    table is saved to the specified output file.

    Example Usage:
    generate_latex_table_info_relaxation_results('relaxation_results.json', 'relaxation_table.tex')
    """
    _text_output = ''
    if os.path.exists(file_json):
        with open(file_json, 'r') as f:
            data_list = json.load(f)

        iline_point_group = 0

        for element in data_list:
            for element_structure in element:
                iline_point_group = iline_point_group + 1
                if iline_point_group == 1:
                    line_gray = ''
                else:
                    iline_point_group = 0
                    line_gray = '\\rowcolor{gray!15} \n'
                _chemical_formula_latex = "\\ce{" + element_structure['unitary_chemical_compound'] + "}"
                _text_output += line_gray
                _text_output += (f"{_chemical_formula_latex} & "
                                 f"{latex_valid_name_for_point_group(element_structure['structure_path'])} & ")
                _text_output += ("{:.2f} & {:.2f} & {:.2f} & {:.2f} & "
                                 "{:.2f} & {:.2f} & {:.2f} & {:.6f} & {:.0f}").format(
                    element_structure['vector_a'],
                    element_structure['vector_b'],
                    element_structure['vector_c'],
                    element_structure['alpha'],
                    element_structure['beta'],
                    element_structure['gamma'],
                    element_structure['layer_thickness'],
                    element_structure['e_unitary'],
                    element_structure['e_relative'])
                _text_output += ' \\\\ \n'
            _text_output += '\\hline'
        with open(file_output, 'w') as latex_file:
            latex_file.write(_text_output)
    else:
        sys.exit(1)
