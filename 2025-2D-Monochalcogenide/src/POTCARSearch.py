import mmap
import os
import re

from CORE import CONST as C


class POTCARScanner:
    """
    Class to scan and search information in POTCAR files.
    """

    def __init__(self):
        """
        Initialize the POTCARScanner class.
        """
        self._file_map = None
        self._path_folder_potpaw = C.PATH_FOLDER_POTPAW
        self._content_file = ''
        self._list_potcar_folders = os.listdir(self._path_folder_potpaw)
        self._path_potcar_file = ''

    def generate_potcar_mapping(self, pattern_folder_name):
        """
        Generate a mapping for the POTCAR file based on the provided folder pattern name.

        :param pattern_folder_name: Pattern folder name to search for POTCAR files.
        """
        if pattern_folder_name in self._list_potcar_folders:
            path_folder_potcar = os.path.join(self._path_folder_potpaw, pattern_folder_name)
            if os.path.exists(path_folder_potcar) and os.path.isdir(path_folder_potcar):
                self._path_potcar_file = os.path.join(str(path_folder_potcar), "POTCAR")
                with open(self._path_potcar_file, 'rb') as POTCAR_M:
                    self._content_file = POTCAR_M.read()
                    self._file_map = mmap.mmap(POTCAR_M.fileno(), 0, access=mmap.ACCESS_READ)

    def search_enmax(self):
        """
        Search for the ENMAX value in the POTCAR file.

        :return: The ENMAX value if found, otherwise None.
        """
        _pattern = re.compile(b'ENMAX')
        _pattern_enmax_value = r'ENMAX\s*=\s*(\d+.\d+)'
        result = self.search(_pattern)
        enmax = re.search(_pattern_enmax_value, result)
        if enmax:
            return float(enmax.group(1))

    def get_content_potcar_file(self):
        """
        Get the content of the POTCAR file.

        :return: The content of the POTCAR file.
        """
        return self._content_file

    def search(self, pattern_search):
        """
        Search for a pattern in the file map.

        :param pattern_search: The pattern to search for.
        :type pattern_search: regex pattern
        :return: The search result.
        :rtype: str
        """
        string_result = ''
        for result in pattern_search.finditer(self._file_map):
            start_r = result.start()
            end_r = result.end()

            line_start = self._file_map.rfind(b'\n', 0, start_r) + 1
            line_end = self._file_map.find(b'\n', end_r)
            string_result = self._file_map[line_start:line_end].decode('utf-8')

        return string_result
