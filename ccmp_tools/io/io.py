from ccmp_tools.base import ABCRegistry
from abc import ABC, abstractmethod

class FileIORegistry(ABCRegistry):
    REGISTRY = {}

class FileIO(metaclass=FileIORegistry):
    _registry_name = 'base'

    @abstractmethod
    def write(self, path, object):
        pass

    @abstractmethod
    def read(self, path):
        pass
