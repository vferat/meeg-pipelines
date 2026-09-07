import os

from mne.datasets import testing

from ..headsurf import MakeHeadSurface
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_make_head_surface():
    make_head_surface = MakeHeadSurface()
    make_head_surface.inputs.subject = "sample"
    make_head_surface.inputs.subjects_dir = os.path.join(testing_dir, "subjects")
    make_head_surface.inputs.overwrite = True
    make_head_surface_results = make_head_surface.run()
