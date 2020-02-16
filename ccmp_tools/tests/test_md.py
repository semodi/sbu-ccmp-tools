"""
Unit and regression test for the md module (molecular dynamics).
"""

# Import package, test suite, and other packages as needed
import ccmp_tools
import pytest
import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))


def test_trajectory_siesta():
    """ Test siesta trajectory"""
    snapshot_path = os.path.join(test_dir, 'siesta_files/test.ANI')
    par_path = os.path.join(test_dir, 'siesta_files/test.fdf')
    mde_path = os.path.join(test_dir, 'siesta_files/test.MDE')

    trajectory = ccmp_tools.md.read_trajectory(snapshot_path, mde_path, par_path)
