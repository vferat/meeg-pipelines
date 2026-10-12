"""Interfaces to `FreeSurfer <https://surfer.nmr.mgh.harvard.edu/>`__.

FreeSurfer is a software suite for the analysis of structural MRI. It is used here
to segment the brain and to reconstruct and process cortical and head surfaces.
"""

from .aparc2aseg import Aparc2Aseg
from .mri_watershed import MRIWatershed
from .mris_smooth import MRIsSmooth
from .mri_mc import MRImc
from .mri_binarize import MRIBinarize
