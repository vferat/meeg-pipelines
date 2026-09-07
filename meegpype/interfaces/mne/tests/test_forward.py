import os

from mne.datasets import testing

from ..forward import MakeForwardSolution
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_make_forward_solution():
    make_forward_solution = MakeForwardSolution()
    make_forward_solution.inputs.fname = "sub-sample-fwd.fif"
    make_forward_solution.inputs.info = os.path.join(
        testing_dir, "MEG", "sample", "sample_audvis_trunc_raw.fif"
    )
    make_forward_solution.inputs.src = os.path.join(
        testing_dir, "subjects", "sample", "bem", "sample-oct-4-src.fif"
    )
    make_forward_solution.inputs.trans = os.path.join(
        testing_dir, "MEG", "sample", "sample_audvis_trunc-trans.fif"
    )
    make_forward_solution.inputs.bem = os.path.join(
        testing_dir, "subjects", "sample", "bem", "sample-1280-bem-sol.fif"
    )
    make_forward_solution.inputs.overwrite = True
    make_forward_solution_results = make_forward_solution.run()
