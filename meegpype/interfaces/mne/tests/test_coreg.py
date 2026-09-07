import os

from mne.datasets import testing

from ..coreg import MakeCoreg
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_make_coreg():
    make_coreg = MakeCoreg()
    make_coreg.inputs.fname = "sample-trans.fif"
    make_coreg.inputs.subject = "sample"
    make_coreg.inputs.subjects_dir = os.path.join(testing_dir, "subjects")
    make_coreg.inputs.info = os.path.join(
        testing_dir, "MEG", "sample", "sample_audvis_trunc_raw.fif"
    )
    make_coreg.inputs.distance = 5 / 1000
    make_coreg.inputs.overwrite = True
    make_coreg_results = make_coreg.run()
