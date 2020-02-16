"""
File input and output
"""

from ccmp_tools.base import ABCRegistry
from abc import ABC, abstractmethod


def read(path, application=''):
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
    compatible_readers = [reader for reader in registry.keys() if ext in reader]
    if not compatible_readers:
        raise Exception('No compatible reading routine found for extension {}'.format(ext))
    elif len(compatible_readers) > 1:
        raise Exception('Ambiguous file extension {}, please also specify application'.format(ext))
    else:
        return registry[compatible_readers[0]]().read(path)


class FileIORegistry(ABCRegistry):
    REGISTRY = {}


class FileIO(metaclass=FileIORegistry):
    """ Abstract base class for classes dealing with
    file input and output
    """

    _registry_name = 'base'

    def write(self, path, object):
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
        pass

    @abstractmethod
    def read(self, path):
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
        pass
