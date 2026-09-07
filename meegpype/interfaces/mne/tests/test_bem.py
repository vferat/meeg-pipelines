import os

from mne.datasets import testing

from ..bem import MakeWatershedBEM, SetupForwardModel
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_make_watershed_bem():
    make_watershed_bem = MakeWatershedBEM()
    make_watershed_bem.inputs.subject = "sample"
    make_watershed_bem.inputs.subjects_dir = os.path.join(testing_dir, "subjects")
    make_watershed_bem.inputs.overwrite = True
    make_watershed_bem_results = make_watershed_bem.run()


def test_setup_forward_model():
    setup_forward_model = SetupForwardModel()
    setup_forward_model.inputs.fname = "sample"
    setup_forward_model.inputs.subject = "sample"
    setup_forward_model.inputs.subjects_dir = os.path.join(testing_dir, "subjects")
    setup_forward_model.inputs.ico = 3
    setup_forward_model.inputs.conductivity = (0.3, 0.006, 0.3)
    setup_forward_model.inputs.verbose = True
    setup_forward_model.inputs.overwrite = True
    setup_forward_model_result = setup_forward_model.run()
