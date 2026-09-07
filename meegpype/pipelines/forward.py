import os
import shutil
from datetime import datetime

from bids.layout import BIDSLayout

from nipype import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype import config, logging

from niworkflows.utils.spaces import SpatialReferences

from ..workflows.forward import init_single_subject_workflow
from ..utils.logs import set_log_level


set_log_level('DEBUG')


def run_forward_pipeline(bids_root,
                         output_dir,
                         subjects,
                         work_dir=None,
                         surface_src=False,
                         volume_src=True,
                         pos=5,
                         n_procs=None):
    # enable logging
    now = datetime.now()
    log = now.strftime("%Y-%m-%d_%H-%M-%S")
    log_directory = os.path.join(output_dir, 'logs', log)
    os.makedirs(log_directory, exist_ok=True)
    config.update_config({'logging': {'log_directory': log_directory,
                                      'log_to_file': True}})
    logging.update_logging(config)

    # Inputs
    n_procs = n_procs or 1
    layout = BIDSLayout(bids_root, validate=False)
    subjects_layout = layout.get_subjects()
    if "emptyroom" in subjects_layout:
        subjects_layout.remove('emptyroom')
    if subjects is None:
        subjects = subjects_layout
    else:
        for subject in subjects:
            subject = subject.strip('sub-')
            if subject not in subjects_layout:
                raise ValueError(f"Subject {subject} not found in BIDS dataset. Available subjects: {subjects_layout}")
        subjects = [subject.strip('sub-') for subject in subjects]

    # Create subjects_dir
    subjects_dir = os.path.join(output_dir, 'sourcedata', 'freesurfer')
    if not os.path.exists(subjects_dir):
        os.makedirs(subjects_dir)

    # copy fsaverage to subjects_dir
    fs_home = os.getenv('FREESURFER_HOME')
    shutil.copytree(os.path.join(fs_home, 'subjects', 'fsaverage'), os.path.join(subjects_dir, 'fsaverage'), dirs_exist_ok=True)

    # Get reference spaces
    spaces = SpatialReferences(['MNI152NLin2009cAsym', 'fsaverage5'])
    spaces.checkpoint()

    # Workflow
    name = 'meegpype_forward'
    wf = Workflow(name=name, base_dir=work_dir)
    inputnode =  Node(IdentityInterface(fields=['subjects_dir']), name='inputnode')
    inputnode.inputs.subjects_dir = subjects_dir

    for subject in subjects:
        subject_wf = init_single_subject_workflow(
                    bids_root=bids_root,
                    output_dir=output_dir,
                    subject=subject,
                    subjects_dir=subjects_dir,
                    spaces=spaces,
                    volume_src=volume_src,
                    surface_src=surface_src,
                    pos=pos
                    )
        wf.connect(inputnode, 'subjects_dir', subject_wf, 'inputnode.subjects_dir')

    # Write graph
    wf.write_graph(graph2use='colored', simple_form=True,dotfilename=os.path.join(log_directory, 'workflow.dot'))

    # Run
    wf.config['execution'] = {'remove_unnecessary_outputs': 'false',
                              'debug': True,
                              'stop_on_first_crash': True,
                              'try_hard_link_datasink': False,
                              'logging': {'workflow_level': 'DEBUG',
                                          'interface_level': 'DEGUB'}}
    wf.run(plugin='MultiProc', plugin_args={'n_procs' : n_procs})
