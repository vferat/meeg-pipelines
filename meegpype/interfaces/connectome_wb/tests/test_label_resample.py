import os

from mne.datasets import testing

from ..label_resample import LabelResample
from ....utils.logs import set_log_level, logger
from ....data import get_data_folder


set_log_level("INFO")
logger.propagate = True

data_dir = get_data_folder()
label_file = os.path.join(data_dir, "fsLR", "atlas_subparc374.L.32k_fs_LR.label.gii")
current_sphere = os.path.join(
    data_dir, "fsLR", "fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii"
)
area_in = os.path.join(
    data_dir, "fsLR", "fs_LR.L.midthickness_va_avg.32k_fs_LR.shape.gii"
)

testing_dir = testing.data_path()
new_sphere = os.path.join(testing_dir, "subjects", "fsaverage", "surf", "lh.sphere")
area_out = os.path.join(
    data_dir, "fsaverage", "fsaverage.L.midthickness_va_avg.164k_fsavg_L.shape.gii"
)


def test_label_resample():
    label_resample = LabelResample()
    label_resample.inputs.label_in = label_file
    label_resample.inputs.current_sphere = current_sphere
    label_resample.inputs.new_sphere = new_sphere
    label_resample.inputs.method = "ADAP_BARY_AREA"
    label_resample.inputs.label_out = "test.label.gii"
    label_resample.inputs.area_metrics = [area_in, area_out]
    label_resample_results = label_resample.run()
