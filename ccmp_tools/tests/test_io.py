
"""
Unit and regression test for the io module (file input and output).
"""

# Import package, test suite, and other packages as needed
import ccmp_tools
import pytest
import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))

@pytest.mark.parametrize("ext", [name.split('_')[-1]\
    for name in ccmp_tools.io.FileIO.get_registry() if 'siesta_' in name])
def test_io_siesta(ext):
    """ Test siesta io routine for all supported file types"""
    path = os.path.join(test_dir, 'siesta_files/test.' + ext )
    ccmp_tools.io.siesta.read(path)
