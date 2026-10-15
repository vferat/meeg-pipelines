"""Custom interfaces, implemented directly in meegpype.

These interfaces do not wrap an external tool: they implement processing steps for
which no existing tool provides the required behavior, such as fitting a deformable
template to a mask to build BEM surfaces.
"""

from .fit_surface import FitSurfaceToMask
