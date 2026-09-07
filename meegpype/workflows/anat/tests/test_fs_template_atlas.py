from mne.datasets import testing

from ..fs_template_atlas import generate_fs_labelling_workflow
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True


subject_id = "S01"
testing_dir = testing.data_path()
subject_dir = "/data/meegpype/freesurfer"


def test_generate_fs_labelling_workflow():
    workflow = generate_fs_labelling_workflow()
    workflow.inputs.inputnode.subject_id = subject_id
    workflow.inputs.inputnode.subjects_dir = subject_dir
    workflow.inputs.inputnode.atlas_name = "Schaefer2018_1000Parcels_7Networks_order"
    workflow.inputs.inputnode.classifier_data_dir = (
        "/meeg-pipelines/meegpype/data/freesurfer"
    )
    workflow.run()
