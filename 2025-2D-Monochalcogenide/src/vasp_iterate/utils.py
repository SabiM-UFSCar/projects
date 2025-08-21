# vasp_iterate/utils.py
"""
Simulações Ab-initio de Materiais - SAbiM
====================
VASP Input Utilities

Author: Marco Aurélio Murbach Teles Machado
Email: murbach@df.ufscar.br
Date: 08/2024
"""

import re
import sys
import datetime
from functools import wraps
from typing import List
from loguru import logger
from config import TOTAL_MQ_SYSTEMS


logger.remove()  # Remove o handler padrão (terminal)


logger.add(
    "./logs/generate_inputs_bc.log",  # log file path
    rotation="150 MB",  # log rotation size 
    level="INFO",  # log level
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"  # format string
)


def log_generate_inputs(func):
    """Decorator that logs function inputs, outputs, and exceptions for debugging.

    Wraps a function to automatically log:
    - Function call details (name and arguments)
    - Successful return values
    - Exceptions with error messages
    Preserves original function metadata using functools.wraps.

    Args:
        func (callable): Function to be decorated

    Returns:
        callable: Wrapped function with logging capability

    Raises:
        Original exception: Re-raises any exception after logging

    Example:
        @log_generate_inputs
        def sample(a, b=2):
            return a * b

        >>> sample(3, b=4)
        # Logs: "Chamando função 'sample' com args=(3,), kwargs={'b': 4}"
        # Logs: "Função 'sample' retornou: 12"
    """
    @wraps(func)  # Preserves original function's metadata (name, docstring, etc.)
    def wrapper(*args, **kwargs):
        # Log entry point with all call parameters
        # Critical for debugging complex function inputs
        logger.info(f"Chamando função '{func.__name__}' com args={args}, kwargs={kwargs}")
        
        try:
            # Execute wrapped function with original arguments
            result = func(*args, **kwargs)
            
            # Log successful result (consider sensitivity for production)
            # Helps verify expected outputs during execution
            logger.info(f"Função '{func.__name__}' retornou: {result}")
            return result
        
        except Exception as e:
            # Log exception details while preserving stack trace
            # Critical for error diagnosis without crashing program
            logger.error(f"Erro em '{func.__name__}': {str(e)}")
            
            # Re-raise to maintain normal exception flow
            # Allows standard error handling upstream
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
    """Converts a date string with textual month abbreviation to DD/MM/YYYY format.

    Parses input strings containing mixed-format dates (e.g., "15 Mai 2023" or "03 Sep 2021")
    and standardizes them to day/month/year numeric format. Handles both German and English
    month abbreviations for compatibility.

    Args:
        string_data (str): Date string containing month abbreviation (e.g., "15 Mai 2023")

    Returns:
        str: Reformatted date in DD/MM/YYYY format (e.g., "15/05/2023")

    Note:
        Requires 're' and 'datetime' modules. Assumes input contains:
        - 3-letter month abbreviation (case-insensitive)
        - 2-digit day
        - 4-digit year
        Will fail if these components are missing.

    Example:
        >>> return_data_formatted_titel("15 Mai 2023")
        "15/05/2023"
    """
    # Month abbreviation to number mapping (supports German/English variants)
    # Handles common bilingual scenarios (e.g., Mai/May, Okt/Oct)
    month = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'Mai': 5, 'May': 5,  # Dual support for German/English
        'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
        'Okt': 10, 'Nov': 11, 'Dez': 12
    }

    # Extract 3-letter month abbreviation (case-insensitive)
    # Critical for handling variable capitalization in input
    return_month_abb = r'([A-z]{3})'
    month_abb = re.search(return_month_abb, string_data).group(1)
    
    # Convert abbreviation to numeric month using mapping
    # Enables language-agnostic month processing
    int_month = month[month_abb]

    # Extract 2-digit day component
    return_day = r'(\d{2})'
    day = re.search(return_day, string_data).group(1)

    # Extract 4-digit year component
    return_year = r'(\d{4})'
    year = re.search(return_year, string_data).group(1)

    # Create datetime object from components
    # Validates date consistency (e.g., rejects invalid day-month combinations)
    date_titel = datetime.datetime(int(year), int(int_month), int(day))
    
    # Format as DD/MM/YYYY (zero-padded day/month)
    date_return = date_titel.strftime("%d/%m/%Y")
    return date_return

def progress_bar_show(current_value: int):
    """Displays a dynamic terminal progress bar tracking task completion percentage.

    Renders a text-based progress bar that updates in-place, showing completion
    status relative to a predefined global total. Automatically completes and
    advances to new line when 100% is reached.

    Args:
        current_value (int): Current progress count (0 to TOTAL_MQ_SYSTEMS)

    Note:
        Relies on global constant TOTAL_MQ_SYSTEMS representing maximum value.
        Uses carriage return (\r) for in-place updates without newlines.
        Progress capped at 100% if current_value exceeds TOTAL_MQ_SYSTEMS.

    Example:
        With TOTAL_MQ_SYSTEMS=100 and current_value=75:
        Progress: [#######################.....................] 75/100 (75.00%)
    """
    # Base label for progress display
    text_info = 'Progress:'
    
    # Fixed visual width of bar component (in characters)
    bar_width = 50
    
    # Calculate completion fraction (clamped 0.0-1.0)
    # Prevents overflow/underflow from incorrect inputs
    percentage = min(1.0, max(0.0, current_value / TOTAL_MQ_SYSTEMS))
    
    # Determine filled bar segments proportional to completion
    # Converts percentage to integer bar units
    filled_length = int(bar_width * percentage)
    
    # Construct bar visualization: filled (#), empty (.), and numeric stats
    # Combines visual elements with precise completion metrics
    bar_string = f"{text_info} [{'#' * filled_length}{'.' * (bar_width - filled_length)}] {current_value}/{TOTAL_MQ_SYSTEMS} ({percentage:.2%})"
    
    # Update current line dynamically (carriage return resets position)
    # Enables live progress animation without scrolling
    sys.stdout.write(f"\r{bar_string}")
    
    # Force immediate display (bypasses output buffering)
    # Ensures real-time visibility during long operations
    sys.stdout.flush()
    
    # Finalize display when reaching 100%
    # Advances cursor to new line after completion
    if current_value == TOTAL_MQ_SYSTEMS:
        print()


def order_dict_by_list(dict_data: dict, order_list: list) -> dict:
    """Orders a dictionary's keys based on a predefined list.

    Args:
        dict_data (dict): Dictionary to be ordered.
        order_list (list): List defining the desired key order.

    Returns:
        dict: New dictionary with keys ordered according to order_list.
              Keys not in order_list are appended at the end in original order.

    Example:
        >>> data = {'b': 2, 'a': 1, 'c': 3}
        >>> order = ['a', 'b']
        >>> order_dict_by_list(data, order)
        {'a': 1, 'b': 2, 'c': 3}
    """
    return {key: dict_data[key] for key in order_list if key in dict_data} | {
        key: dict_data[key] for key in dict_data if key not in order_list
    }