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
