from .io import FileIO
from ase.io import read as ase_read
from ase.io import write as ase_write
import os


def read(path):
    #detect extension
    ext = path.split('.')[-1]
    registry = FileIO.get_registry()
    if not 'siesta_' + ext in registry:
        raise Exception('No routine implemented to read SIESTA {} files'.format(ext))
    else:
        return registry['siesta_' + ext]().read(path)


class SiestaIO(FileIO):
    _registry_name = 'siesta'


class AniIO(SiestaIO):
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
