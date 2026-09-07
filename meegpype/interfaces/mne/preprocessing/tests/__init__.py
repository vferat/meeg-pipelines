import os

from meegpype.interfaces.mne.coreg import MakeCoreg
from mne.datasets import testing

from ..filter_chpi import FilterChpi
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_make_coreg():
    filter_chpi = FilterChpi()
    filter_chpi.inputs.raw = os.path.join(testing_dir, "MEG", "sample", "sample_audvis_trunc_raw.fif")
    filter_chpi.inputs.include_line = True
    filter_chpi.inputs.t_step = 0.01
    filter_chpi.inputs.t_window = 'auto'
    filter_chpi.inputs.ext_order = 1
    filter_chpi.inputs.allow_line_only = False
    filter_chpi.inputs.overwrite = True
    filter_chpi_results = filter_chpi.run()
