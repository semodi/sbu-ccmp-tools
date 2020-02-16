"""
Trajectory class that bundles all information about a MD/Phonon/Geometry opt. run
"""
import numpy as np
import ase
from ccmp_tools.io import read
from ase.calculators.singlepoint import SinglePointCalculator


def read_trajectory(trajectory_path, property_path=None, parameter_path=None):
    """ Read MD/Phonon/GO trajectory from file and optionally also
    read parameter_path for simulation parameters
    """

    snapshots = read(trajectory_path)

    if parameter_path:
        parameters = read(parameter_path)
    else:
        parameters = {}

    if property_path:
        properties = read(property_path)
    else:
        properties = None

    return Trajectory(snapshots, parameters, properties)


class Trajectory():
    """ Trajectory class bundling positions, properties such as energy and pressure
    as well as simulation parameters such as the box size, time step, type of run
    etc.

    Parameters
    ----------
    snapshots: ase.Atoms or list thereof
        System snapshot for every time step
    parameters: dict
        Simulation parameters
    properties: pandas.DataFrame
        System properties such as energy, pressure etc.

    """

    def __init__(self, snapshots, parameters={}, properties=None):

        if not isinstance(snapshots, list):
            if isinstance(snapshots, ase.Atoms):
                snapshots = [snapshots]
            else:
                raise ValueError('Snapshots should either be a single ase.Atoms object or a list thereof')

        self._snapshots = snapshots

        #Parameter defaults
        self._parameters = {'md.typeofrun': 'Verlet'}
        if parameters:
            self._parameters.update(parameters)
        self._properties = properties

        for snapshot, property in zip(self._snapshots, properties.iterrows()):
            snapshot.calc = SinglePointCalculator(snapshot)
            snapshot.calc.results = dict(property[1])
            if 'E_pot' in snapshot.calc.results:
                snapshot.calc.results['energy'] = snapshot.calc.results['E_pot']
        # self.parameters.update(kwargs)

    def _determine_cell(self):
        #TODO: Different ways to provide unitcell
        if 'latticeconstant' in self._parameters and\
            'latticevectors' in self._parameters:
            lat_const = self._parameters['latticeconstant'][0]
            lat_vec = self._parameters['latticevectors']
            return lat_const * np.array(lat_vec)
        else:
            diff = np.max(self.positions, axis=0) - np.min(self.positions, axis=0)
            cell = np.eye(3)
            cell = [cell[i, i] * diff[i] + (diff[i] * 0.1) for i in range(3)]
            return cell

    def get_positions(self):
        positions = []
        for snapshot in self._snapshots:
            positions.append(snapshot.get_positions())
        return np.array(positions)

    def get_chemical_symbols(self):
        chem_symbols = []
        for snapshot in self._snapshots:
            chem_symbols.append(snapshot.get_chemical_symbols())
        return chem_symbols

    def get_property(self, property=None):
        """
        Returns a system property such as energy, pressure etc.
        If no property specified, prints a list of available properties
        for this system

        Parameters
        ----------
        property: str, optional
            Property to return, if None print options

        Returns
        -------
        properties, numpy.ndarray or None
            Requested properties if not None

        """
        if not property:
            print(self._snapshots[0].calc.results.keys())
        else:
            properties = []
            for snapshot in self._snapshots:
                properties.append(snapshot.calc.results[property])
            return np.array(properties)

    @property
    def cell(self):
        return self._determine_cell()

    @property
    def snapshots(self):
        return self._snapshots

    @property
    def parameters(self):
        return self._parameters

    @property
    def properties(self):
        return self._properties

    @property
    def species(self):
        return self.get_chemical_symbols()

    @property
    def n_steps(self):
        return len(self._snapshots)

    @property
    def n_atoms(self):
        return len(self.positions[0])

    @property
    def n_species(self):
        return len(np.unique(self.species[0]))

    @property
    def positions(self):
        return self.get_positions()
