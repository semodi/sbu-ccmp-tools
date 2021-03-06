#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 20:50:35 2020

@author: awills
"""
import sisl, os, sys
from tqdm import tqdm
import numpy as np
import MDAnalysis as MD

class Simulation():
    '''Base class to build other simulations from, primarily for utility functions
    like _filefind and others in the future.
    '''
    def __init__(self):
        pass
    
    def _filefind(self, attrp, fext, attr):
        '''
        Parameters
        ----------
        attrp : arbitrary
            Input to method to be evaluated by bool().
            If bool(attrp) is True:
                If type(attrp) == str and fext in attrp:
                    the method searches attrp for the file extension fext.
                    If found, the method assumes this is a file path relative to self.path
                    and sets self.attr = os.path.join(self.path, attrp)
                If attrp is not a string or the file extension is not in the string:
                    the method searches self.path for the file extension and assumes whatever is found is the file desired
                    and sets os.path.join(self.path, the first file with matching extension found)
                    If the file is not found, an error is caught and self.attr is set to None
        fext : str
            The extension of the file to find.
        attr : str
            The attribute to set with self.__setattr__(), which determines what it will be retrieved with.

        Returns
        -------
        None. Attributes are set in-place, and if nothing is found then self.attr = None.

        '''
        #if attr is non-false, look for it in sim directory
        if attrp:
            #if fext in attr, assume filename
            if (type(attrp) == str) and (fext in attrp):
                self.__setattr__(attr, os.path.join(self.path, attrp) if type(attrp)==str and fext in attrp.lower() else None)
            #else if just T/non-F, look for it
            else:
                try:
                    self.__setattr__(attr, os.path.join(self.path,
                                                        [i for i in os.listdir(self.path) if fext.lower() in i.lower()][0]))
                except IndexError:
                    #if there is no zero index, empty list and file not found
                    print("attribute not found: {} ending in {}".format(attr, fext))
                    self.__setattr__(attr, None)
        else:
            #keep whatever false value
            self.__setattr__(attr, None)
    

class SiestaSimulation(Simulation):
    def __init__(self, path, fdfb=True, fdfext='.fdf'):
        '''
        Parameters
        ----------
        path : str
            Root directory for the simulation, assuming the directory is populated by files generated by 
            a siesta command.
        fdfb : arbitrary, optional
            Either a string with SimulationLabel.fdf or a value to be checked by bool(). 
            The default is True.
        fdfext : str, optional
            The extension for your FDF file, if not standard. The default is '.fdf'.

        Returns
        -------
        None. Updates object in-place:
            If fdf is a (non-empty) string and a file in self.path with matching fdfext(ension) is found as an extension,
                this sets self.fdfp(ath) to input and self.fdf as a SISL SILE object
            If fdf is is not a string, or is a string without matching fdfext(ension),
                we look for a file in self.path with matching fdfext(ension) and set self.fdfp as the matching file
                and self.fdf as the SISL SILE object returned  with that path.
            
            If the fdf retrieval is successful, many attributes are retrieved from the SISL object.
                If the default keys we search for are absent, the SISL object returns None.
                
            If the file is not found or specified as False, we set self.fdfp and self.fdf as None.

        '''
        #base directory of simulation
        self.path = path

        #fdf can be read in automatically if found; default is specified
        self._filefind(attrp=fdfb, fext=fdfext, attr='fdfp')
        #set sisl fdf reader
        self.fdf = sisl.get_sile(self.fdfp) if self.fdfp else None
        #if fdf found, can specify numerous things about the simulation
        if self.fdf:
            # TODO: expand data read in, add functionality for user input keys to .get()
            self.simlabel = self.fdf.get("SimulationLabel")
            self.latticeconstant = self.fdf.get('LatticeConstant')
            self.latticevectors = np.array([float(v) for i in self.fdf.get("LatticeVectors") for v in i.split()]).reshape(3,3)
            self.dt = self.fdf.get('MD.LengthTimeStep')
            self.istep = self.fdf.get("MD.InitialTimeStep")
            self.fstep = self.fdf.get("MD.FinalTimeStep")
            #if both are specified, find number of steps
            if self.istep and self.fstep:
                self.nsteps = self.fdf.get("MD.FinalTimeStep") - self.fdf.get("MD.InitialTimeStep") + 1 #inclusive of first step
            #if only final is specified
            elif self.fstep and not self.istep:
                self.nsteps = self.fstep
            #if number of steps, assume MD simulation as opposed to GO or other
            if self.nsteps:
                self.simtype= 'md'
            self.mdtype = self.fdf.get("MD.TypeOfRun")
            #if mdtype is FC, this is a phonon calculation
            if self.mdtype.lower() == 'FC'.lower():
                self.simtype = 'phonon'
            #if mdtype is CG, Broyden, or FIRE then it's GO
            if self.mdtype.lower() in ['cg', 'broyden', 'fire']:
                self.simtype = 'go'
            self.natoms = self.fdf.get("NumberOfAtoms")
            self.nspecies = self.fdf.get("NumberOfSpecies")
            self.chemspeclab = [i.split() for i in self.fdf.get("ChemicalSpeciesLabel")]
        
    def iMD(self, ani=None, fext='.ANI', defaultcell=True):
        '''
        Parameters
        ----------
        ani : arbitrary, optional
            Either a string with SimulationLabel.ANI or a value to be checked by bool(). 
            The default is None.
        fext : str, optional
            The extension for your ANI file, if not standard. The default is '.ANI'.
        defaultcell : bool, optional
            * Only used if self.fdf and self.latticeconstant and self.latticevectors are not False*
            If True, an estimation of the simulation cell size is made.
            The estimation is made by making a cubic cell 10% larger than the largest displacement along the trajectory.
            The default is True.

        Returns
        -------
        None. Updates object in-place:
            If ani is a (non-empty) string and a file in self.path with matching aniext(ension) is found as an extension,
                this sets self.anip(ath) to input and self.ani as an MDAnalysis.Universe object
            If ani is is not a string, or is a string without matching aniext(ension),
                we look for a file in self.path with matching aniext(ension) and set self.anip as the matching file
                and self.ani as the MDAnalysis.Universe object returned  with that path.
            If the file is not found or specified as False, we set self.anip as None.
            
            If the file is found an a Universe is made:
                If an FDF is already set with cell dimensions and a timestep specified,
                we update the Universe and its trajectory to include relevant information.
                If there is no FDF information, we populate with assumed defaults:
                    dt = 0.5 ps
                    MD simulation with Verlet time evolution
                    natoms, nsteps, and nspecies dependent on the input .ANI
                    The default cell dependent on maximum displacement between coordinates in trajectory.
                        *This is likely to GREATLY overestimate cell size when coordinates are not wrapped.*
        '''
        #first look for ani file
        self._filefind(ani, fext, 'anip')
        #make sure there is one
        assert self.anip, "{} file not found in simulation directory.".format(fext)
        if (self.fdf) and (self.latticeconstant) and (self.latticevectors.tolist()):
            self.universe = MD.Universe(self.anip, topology_format='xyz',
                                        format='xyz', dt=self.dt)
            #update topology with information from fdf
            #triclinic_dimensions attribute to allow cell specification for generic cell
            self.universe.triclinic_dimensions = self.latticeconstant*self.latticevectors
            #default to femtoseconds in siesta
            self.universe.trajectory.units['time'] = 'fs'
        else:
            self.universe = MD.Universe(self.anip, topology_format='xyz',
                                        format='xyz', dt=0.5)
            #populate default assumptions
            self.simtype = "md"
            self.mdtype = "verlet"
            self.natoms = self.universe.trajectory.n_atoms
            self.nsteps = self.universe.trajectory.n_frames
            self.nspecies = len(set(self.universe.atoms.types))
            if defaultcell:
                mins = []
                maxs = []
                #this will GREATLY overestimate size if a periodic calculation's coordinate output 
                #is not wrapped
                print("Calculating default cell...")
                for frame in tqdm(self.universe.trajectory, file=sys.stdout):
                    xyz = frame.positions
                    maxs.append(xyz.max())
                    mins.append(xyz.min())
                cell_size = max(maxs) - min(mins)
                #set size to 10% greater than max-min of coordinates, cubic
                self.universe.dimensions = 3*[cell_size*1.1] + 3*[90]
                    
    def iMDE(self, mde=None, fext='.MDE'):
        '''
        Parameters
        ----------
        mde : arbitrary, optional
            Either a string with SimulationLabel.MDE or a value to be checked by bool(). 
            The default is None.
        fext : str, optional
            The file extension for the MDE file, if not standard. The default is '.MDE'.

        Returns
        -------
        None. Updates object in-place:
            IF FOUND: 
                COLUMNS ARE Step, T (K), E_KS (eV), E_tot (eV), Vol (A^3), P (kBar)
            If mde is a (non-empty) string and a file in self.path with matching mdeext(ension) is found as an extension,
                this sets self.mdep(ath) to input and self.mde as an np.ndarray object with shape (nsteps, 6)
            If mde is is not a string, or is a string without matching mdeext(ension),
                we look for a file in self.path with matching mdeext(ension) and set self.mdep as the matching file
                and self.mde as the np.ndarray object with shape (nsteps, 6) with that path.
            If the file is not found or specified as False, we set self.mdep as None.
        '''
        #first look for mde file
        self._filefind(mde, fext, 'mdep')
        #make sure there is one
        assert self.mdep, '{} file not found in simulation directory.'.format(fext)
        self.mde = np.loadtxt(os.path.join(self.path, self.mdep),
                              comments='#')