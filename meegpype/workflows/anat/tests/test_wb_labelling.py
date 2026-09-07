import os

from mne.datasets import testing

from ..wb_labelling import generate_wb_labelling_workflow
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_generate_meeg_forward_workflow():
    workflow = generate_wb_labelling_workflow()
    workflow.inputs.inputnode.atlas = "subparc374"
    workflow.inputs.inputnode.subject = "sample"
    workflow.inputs.inputnode.subjects_dir = os.path.join(testing_dir, "subjects")
    workflow.run()
