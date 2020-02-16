"""
File input and output
"""

from ccmp_tools.base import ABCRegistry
from abc import ABC, abstractmethod


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
