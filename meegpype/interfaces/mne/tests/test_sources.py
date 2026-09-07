import os

from mne.datasets import testing

from ..sources import (
    SetupSurfaceSourceSpace,
    SetupVolumeSourceSpace,
    CombineSourceSpaces,
)
from ....utils.logs import set_log_level, logger

set_log_level("INFO")
logger.propagate = True

testing_dir = testing.data_path()


def test_setup_surface_source_space():
    setup_source_space = SetupSurfaceSourceSpace()
    setup_source_space.inputs.fname = "sub-sample_sources-surface-src.fif"
    setup_source_space.inputs.subject = "sample"
    setup_source_space.inputs.subjects_dir = os.path.join(testing_dir, "subjects")
    setup_source_space.inputs.spacing = "oct5"
    setup_source_space.inputs.add_dist = "patch"
    setup_source_space.inputs.n_jobs = 2
    setup_source_space.inputs.overwrite = True
    setup_source_space.inputs.verbose = True
    setup_source_space_results = setup_source_space.run()


def test_setup_volume_source_space():
    setup_volume_source_space = SetupVolumeSourceSpace()
    setup_volume_source_space.inputs.subject = "sample"
    setup_volume_source_space.inputs.fname = "sub-sample_sources-volume-src.fif"
    setup_volume_source_space.inputs.subjects_dir = os.path.join(
        testing_dir, "subjects"
    )
    setup_volume_source_space.inputs.overwrite = True
    setup_volume_source_space.inputs.bem = os.path.join(
        testing_dir, "subjects", "sample", "bem", "sample-1280-bem.fif"
    )
    setup_volume_source_space.inputs.volume_label = [
        "Right-Cerebellum-Cortex",
        "Left-Cerebellum-Cortex",
    ]
    setup_volume_source_space_results = setup_volume_source_space.run()


def test_combine_sources():
    combine_sources = CombineSourceSpaces()
    combine_sources.inputs.fname = "sub-sample_sources-combined-src.fif"
    combine_sources.inputs.sources = [
        os.path.join(testing_dir, "subjects", "sample", "bem", "sample-oct-4-src.fif"),
        os.path.join(testing_dir, "subjects", "sample", "bem", "sample-oct-2-src.fif"),
    ]
    combine_sources.inputs.overwrite = True
    combine_sources.inputs.verbose = True
    combine_sources_results = combine_sources.run()
