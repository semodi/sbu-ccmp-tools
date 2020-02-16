"""
File input and output for SIESTA related files
"""
from .io import FileIO
from ase.io import read as ase_read
from ase.io import write as ase_write
import os


def read(path):
    """ Detects file type by extension and uses appropriate
    FileIO child class to read content

    Parameters
    ----------
    path: string
        Path to file

    Returns
    -------
    File content
    """
    #detect extension
    ext = path.split('.')[-1]
    registry = FileIO.get_registry()
    if not 'siesta_' + ext in registry:
        raise Exception('No routine implemented to read SIESTA {} files'.format(ext))
    else:
        return registry['siesta_' + ext]().read(path)


class SiestaIO(FileIO):
    _registry_name = 'siesta'


class AniIO(FileIO):
    """ FileIO class to read SIESTA .ANI files
    """
    _registry_name = 'siesta_ANI'

    def read(self, path):
        assert path.split('.')[-1] == 'ANI'
        xyz_path = path.replace('ANI', 'xyz')
        try:
            os.symlink(path, xyz_path)
        except FileExistsError:
            os.remove(xyz_path)
            os.symlink(path, xyz_path)
        atoms = ase_read(xyz_path,':')
        os.remove(xyz_path)
        return atoms

class FdfIO(FileIO):
    """ FileIO class to read SIESTA .fdf files
    """
    _registry_name = 'siesta_fdf'

    def read(self, path):
        content = {}

        with open(path, 'r') as file:
            for entry in self.next_fdf_entry(file):
                key, value = entry[1].popitem()
                value = self.parse_entry(value, entry[0])
                content[key] = value

        return content

    @staticmethod
    def parse_entry(entry, block=False):
        """ Given an entry, parse it with a given hierarchy of transformations:
            (int, float, (float, string), boolean, string). Tries to transform
            fdf blocks into arrays

        Parameters
        ----------
        entry, str
            fdf entry to parse
        block, boolean
            whether entry is from fdf block

        Returns
        -------
        Parse entry
            File type depends on which parsing transformation was successful
        """
        # Hierarchy of parsing functions
        transformations = [lambda x: int(x),
                           lambda x: float(x),
                           lambda x: (float(x.split()[0]),' '.join(x.split()[1:])),
                           lambda x: {'t' : True,'f' : False,
                            '.false.': False, '.true.': True}[x.lower()]]

        def apply_transformations(x):
            for t in transformations:
                try:
                    x= t(x)
                    break
                except Exception:
                    continue
            return x

        if block:
            entry = entry.split('\n')
            for i, line in enumerate(entry):
                entry[i] = line.split()
                for j, element in enumerate(entry[i]):
                    entry[i][j] = apply_transformations(element)
            # remove empty lines
            entry = [e for e in entry if e]

        else:
            entry = apply_transformations(entry)

        return entry

    @staticmethod
    def next_fdf_entry(file):
        """ Returns an iterator over entries in SIESTA .fdf file

        Parameters
        ----------
        file, File Buffer
            opened .fdf file

        Returns
        -------
        iterator
            Returns a tuple (boolean, dict) where boolean indicates whether
            a fdf %block was returned and dict gives a fdf key value pair
        """
        inside_block = False
        block_content = ''
        block_name = ''
        line = file.readline()
        while (line):
            if len(line.strip()) > 0:
                if line.strip()[0] == '%':
                    if not inside_block:
                        block_name = ' '.join(line.split()[1:]).lower()
                    else:
                        block_out = block_content
                        block_content = ''
                        yield True, {block_name: block_out}

                    inside_block = (not inside_block)
                elif not inside_block:
                    yield False, {line.split()[0].lower(): ' '.join(line.split()[1:])}
                else:
                    block_content += line

            line = file.readline()
