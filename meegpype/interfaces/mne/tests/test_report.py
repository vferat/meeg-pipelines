import os

from mne.datasets import testing

from ..report import MakeReport
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_make_watershed_bem():
    # TODO: change path of files
    make_report = MakeReport()
    make_report.inputs.fname = "sub-sample-report.h5"
    make_report.inputs.subject = "sample"
    make_report.inputs.subjects_dir = os.path.join(testing_dir, "subjects")
    make_report.inputs.info = os.path.join(
        testing_dir, "MEG", "sample", "sample_audvis_trunc_raw.fif"
    )
    make_report.inputs.trans = os.path.join(
        testing_dir, "MEG", "sample", "sample_audvis_trunc-trans.fif"
    )
    make_report.inputs.bem = os.path.join(
        testing_dir, "subjects", "sample", "bem", "sample-1280-bem-sol.fif"
    )
    make_report.inputs.forward = os.path.join(
        testing_dir, "MEG", "sample", "sample_audvis_trunc-meg-eeg-oct-4-fwd.fif"
    )
    make_report.inputs.overwrite = True
    make_report_results = make_report.run()
