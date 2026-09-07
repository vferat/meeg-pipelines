import os
from datetime import datetime

from nipype import config, logging, Node
from nipype.interfaces.io import DataSink

from ..workflows.anat.wb_labelling import generate_wb_labelling_workflow
from ..utils.logs import set_log_level
from ..utils._checks import ensure_path, ensure_subject, ensure_int, check_value
from ..data.fsLR import ATLAS


def run_fslr_pipeline(atlas, subject, subjects_dir, output_dir, work_dir=None, n_procs=None):
     # enable logging
    now = datetime.now()
    log = now.strftime("%Y-%m-%d_%H-%M-%S")
    log_directory = os.path.join(output_dir, 'logs', log)
    os.makedirs(log_directory, exist_ok=True)
    config.update_config({'logging': {'log_directory': log_directory,
                                      'log_to_file': True}})
    logging.update_logging(config)

    # Validate inputs
    atlas = atlas
    ATLAS_NAMES = [item["name"] for item in ATLAS]
    check_value(atlas, ATLAS_NAMES, "atlas")
    subject = ensure_subject(subject)
    subjects_dir = ensure_path(subjects_dir, must_exist=True)
    output_dir = ensure_path(output_dir, must_exist=False)
    if work_dir is not None:
        work_dir = ensure_path(work_dir, must_exist=False)
    if n_procs is not None:
        n_procs =  ensure_int(n_procs)
    else:
        n_procs = 1

    wf = generate_wb_labelling_workflow(name='fslr_workflow', base_dir=work_dir)
    wf.inputs.inputnode.atlas = atlas
    wf.inputs.inputnode.subject = subject
    wf.inputs.inputnode.subjects_dir = subjects_dir

    # datasink
    datasink = Node(
        DataSink(base_directory=output_dir, container=subject),
        name="datasink",
    )
    wf.connect(
        wf.get_node("outputnode"), "aseg", datasink, "anat.@aseg"
    )
    wf.connect(
        wf.get_node("outputnode"), "annot_lh", datasink, "anat.@lh_aseg"
    )
    wf.connect(
        wf.get_node("outputnode"), "annot_rh", datasink, "anat.@rh_aseg"
    )
    wf.connect(
        wf.get_node("outputnode"), "LUT", datasink, "anat.@lut"
    )

    # Run
    wf.config['execution'] = {'remove_unnecessary_outputs': 'false', 'debug': True, 'stop_on_first_crash': True}
    wf.run(plugin='MultiProc', plugin_args={'n_procs' : n_procs})
    return

