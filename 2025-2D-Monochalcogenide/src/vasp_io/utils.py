# vasp_io/utils.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
VASP Input Utilities

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import re
import datetime
from functools import wraps
from typing import List
from loguru import logger


logger.remove()  # Remove o handler padrão (terminal)


logger.add(
    "./logs/generate_inputs.log",  # Arquivo de log
    rotation="10 MB",  # Rotaciona o log a cada 10MB
    level="INFO",  # Nível de log
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"  # Formato
)


def log_generate_inputs(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Chamando função '{func.__name__}' com args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Função '{func.__name__}' retornou: {result}")
            return result
        except Exception as e:
            logger.error(f"Erro em '{func.__name__}': {str(e)}")
            raise
    return wrapper


def get_mq_elements(mq: str) -> List[str]:
    """
    Extract chemical elements from a material's name (e.g., 'AlS' -> ['Al', 'S']).

    Args:
        mq (str): Material name in the format 'Element1Element2' (e.g., 'GaTe', 'SiSe').
                  Case-sensitive (must follow [A-Z][a-z]* convention).

    Returns:
        List[str]: List of extracted elements in order of appearance.

    Raises:
        ValueError: If input is empty or contains non-alphabetic characters.

    Examples:
        >>> get_mq_elements('AlSe')
        ['Al', 'Se']
        >>> get_mq_elements('SnTe')
        ['Sn', 'Te']
    """
    if not mq or not mq.isalpha():
        raise ValueError("Material name must be non-empty alphabetic string (e.g., 'GaS')")

    chem_composition_re = re.compile(r"([A-Z][a-z]*)")
    elements = chem_composition_re.findall(mq)
    
    if not elements:
        raise ValueError(f"No valid elements found in '{mq}'. Expected format like 'AlS'.")
    
    return elements


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