"""
sbu-ccmp-tools
 Libary of utilites to analyze the ouput of electronic structure programs 
"""

# Add imports here
from .ccmp_tools import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
