import os
import time
from typing import List

import psutil

running = True


def list_orderby(list_to_sort, sorting_key, ascending=True):
    """
    Sorts a list of dictionaries based on a specified sorting key.

    :param list_to_sort: The list of dictionaries to be sorted.
    :param sorting_key: The key based on which the sorting will be performed.
    :param ascending: A boolean flag indicating whether the sorting should be in ascending order (default is True).

    :return: A new list containing the dictionaries sorted according to the specified key.

    Example Usage:
    sorted_list = list_orderby(my_list, 'age', ascending=False)
    """
    try:
        if ascending:
            list_order = sorted(list_to_sort, key=lambda x: x[sorting_key])
        else:
            list_order = sorted(list_to_sort, key=lambda x: x[sorting_key], reverse=True)
        return list_order
    except (TypeError, KeyError):
        print('Unable to sort the list. Please check if the list elements are sortable and the sorting key is valid.')
        return []


def expand_folders_path(list_folders, path_root, subfolder=None):
    """
    Expand folder paths.

    :param list_folders: List of folder names.
    :param path_root: Root path for the folders.
    :param subfolder Name of the subfolder. Defaults to None.

    :return: List of expanded folder paths.

    Example Usage:
    list_folders = expand_folders_path(list_folders, '/path/to/folder')
    list_folders = expand_folders_path(list_folders, '/path/to/folder', 'subfolder/name')
    """
    list_path_folders = []
    list_path_subfolder = []

    for folder in list_folders:
        list_path_folders.append(os.path.join(path_root, folder))

    if subfolder is not None:
        for path_folder in list_path_folders:
            list_path_subfolder.append(os.path.join(str(path_folder), subfolder))
        return list_path_subfolder
    else:
        return list_path_folders


def list_first_folders(directory: str) -> List[str]:
    """
    Lists the first-level folders (directories) in the specified directory.

    :param directory: The path of the directory to search.

    :return: A list of the first-level folders (directories) found in the specified directory.

    Example Usage:
    list_folders = list_first_folders('/path/to/folder')
    """
    list_files = os.listdir(directory)

    list_folders = [folder for folder in list_files if os.path.isdir(os.path.join(directory, folder))]
    return list_folders


def list_folders_recursively(folder_path: str) -> List[str]:
    """
    List all folders recursively.

    :param folder_path: The path to the directory to be traversed.

    :return: A list of strings representing the full paths of all folders found.

    Example Usage:
    list_folders = list_folders_recursively('/path/to/folder')
    """
    list_folders = []
    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            list_folders.append(os.path.join(root, directory))
    return list_folders


def list_last_folders_recursively(folder_path: str) -> List[str]:
    """
    List the last folders in each hierarchy recursively.

    :param folder_path: The path to the directory to be traversed.

    :return: A list of strings representing the full paths of the last folders in each hierarchy.

    Example Usage:
    list_folders = list_last_folders_recursively('/path/to/folder')
    """
    last_folders = []

    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            sub_folders = os.listdir(os.path.join(root, directory))
            if not any(os.path.isdir(os.path.join(root, directory, sub_folder)) for sub_folder in sub_folders):
                last_folders.append(os.path.join(root, directory))
    return last_folders


def watch_resource_usage():
    """
    Continuously monitors CPU, memory, and disk usage.

    This function runs indefinitely, periodically retrieving and displaying the current CPU, memory, and disk usage.

    Example Usage:
    watch_resource_usage()

    Output:
    CPU Usage: 20.1% | Memory Usage: 45.8%
    Number of CPU Cores: 4
    Disk Usage: 60.2%

    Dependencies:
    - psutil: A cross-platform library for retrieving information on running processes, system utilization,
    and disk usage.

    Note:
    The function uses the `psutil` library to obtain CPU, memory, and disk usage metrics and prints the information
    to the console.
    The monitoring interval is set to 5 seconds, but can be adjusted by modifying the `time.sleep` duration.
    Additional system metrics such as the number of CPU cores and disk usage percentage are also displayed.
    """
    global running
    while running:
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        print(f"CPU Usage: {cpu_percent}% | Memory Usage: {memory_percent}%")
        print("Number of CPU Cores: {}".format(psutil.cpu_count()))
        print("Disk Usage: {}%".format(psutil.disk_usage('/').percent))
        time.sleep(1)


def stop_watch_resource_usage():
    """
    Stops the resource usage monitoring.

    This function sets the global variable `running` to `False`, which interrupts the execution
    of the resource usage monitoring loop in the `watch_resource_usage()` function.

    Example Usage:
    stop_watch_resource_usage()

    Dependencies:
    - The `running` variable is assumed to be defined globally in the context where
      `watch_resource_usage()` function is running.

    Note:
    Calling this function will halt the monitoring of CPU and memory usage by setting
    the flag `running` to `False`, causing the `watch_resource_usage()` function to exit its loop.
    """
    global running
    running = False


def extract_values_from_string(str_pattern, values_list):
    """
    Extracts values from a string pattern based on a list of possible values.

    Parameters:
    :param str_pattern: The string pattern to search for values.
    :param values_list: List of possible values to extract.

    :return: extracted_values (str): Extracted value from the string pattern.
    """
    extracted_values = ''
    for value in values_list:
        if value in str_pattern:
            extracted_values = value
    return extracted_values
