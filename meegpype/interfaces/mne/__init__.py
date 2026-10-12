"""Interfaces to `MNE-Python <https://mne.tools/>`__.

MNE-Python is a Python package for the analysis of MEG and EEG data. It is used here
for preprocessing (Maxwell filtering, head position), BEM and source space setup,
forward modelling and reporting.
"""

from .preprocessing import (
    ComputeHeadPos,
    ApplyMaxwellFilter,
    ComputeDestination,
    FilterChpi,
)
from .bem import MakeWatershedBEM, SetupForwardModel
from .sources import (
    SetupSurfaceSourceSpace,
    SetupVolumeSourceSpace,
    CombineSourceSpaces,
)
from .coreg import MakeCoreg
from .forward import MakeForwardSolution
from .report import MakeReport
from .fiducials import ApplyTransform
from .headsurf import MakeHeadSurface
from .decimate_surface import DecimateSurface
