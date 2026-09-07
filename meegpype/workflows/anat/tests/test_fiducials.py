import os

from mne.datasets import testing

from ..fiducials import generate_fiducials_workflow
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()
subject_dir = os.path.join(testing_dir, "subjects")


def test_generate_fiducials_workflow():
    workflow = generate_fiducials_workflow()
    workflow.inputs.inputs_node.fiducials = {
        "NAS": [127, 213, 139],
        "LPA": [52, 113, 96],
        "RPA": [202, 113, 91],
    }
    workflow.inputs.inputs_node.T1w = os.path.join(
        subject_dir, "fsaverage", "mri", "T1.mgz"
    )
    workflow.inputs.inputs_node.fsnative = os.path.join(
        subject_dir, "sample", "mri", "T1.mgz"
    )
    workflow.run()
