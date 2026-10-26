import os
from datetime import datetime

from nipype import config, logging

from ..workflows.anat.bem import generate_bem_workflow
from ..utils.logs import set_log_level
from ..utils._checks import ensure_path, ensure_subject, ensure_int, check_value

set_log_level('DEBUG')

BEM_METHODS = ("basic", "refined")


def run_bem_pipeline(subject, subjects_dir, method="basic", work_dir=None, n_procs=None):
    """Compute the BEM surfaces of a FreeSurfer subject.

    The surfaces are written to ``subjects_dir/subject/bem``.
    """
    # Validate inputs
    check_value(method, BEM_METHODS, "method")
    subjects_dir = ensure_path(subjects_dir, must_exist=True)
    subject = ensure_subject(subject, subjects_dir)
    if work_dir is not None:
        work_dir = ensure_path(work_dir, must_exist=False)
    if n_procs is not None:
        n_procs = ensure_int(n_procs)
    else:
        n_procs = 1

    # enable logging
    if work_dir is not None:
        now = datetime.now()
        log = now.strftime("%Y-%m-%d_%H-%M-%S")
        log_directory = os.path.join(work_dir, 'logs', log)
        os.makedirs(log_directory, exist_ok=True)
        config.update_config({'logging': {'log_directory': log_directory,
                                          'log_to_file': True}})
        logging.update_logging(config)

    wf = generate_bem_workflow(subject_id=subject,
                               subjects_dir=str(subjects_dir),
                               name='bem_workflow',
                               method=method)
    wf.base_dir = str(work_dir) if work_dir is not None else None

    # Run
    wf.config['execution'] = {'remove_unnecessary_outputs': 'false', 'debug': True, 'stop_on_first_crash': True}
    wf.run(plugin='MultiProc', plugin_args={'n_procs': n_procs})
    return
