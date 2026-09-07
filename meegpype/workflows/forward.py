import os

from nipype import Node, Workflow, DataSink
from nipype.interfaces.utility import IdentityInterface

from niworkflows.utils.spaces import Reference
from smriprep.workflows.anatomical import  init_anat_preproc_wf

from meegpype.utils.bids import collect_subject_data
from meegpype.workflows.meg.maxwell import init_maxwell_wf
from meegpype.workflows.meg.anat import init_meg_anat_wf
from meegpype.workflows.anat.fiducials import init_fiducials_wf

from meegpype.interfaces.mne import (
    MakeCoreg,
    MakeForwardSolution,
    MakeReport
)


def init_single_subject_workflow(bids_root, output_dir, subject, subjects_dir, spaces,
                                 volume_src=True, pos=5, surface_src=False):

    subject_dir = os.path.join(output_dir, f'sub-{subject}')
    subject_data = collect_subject_data(bids_root, subject)

    wf = Workflow(name=f'sub_{subject}_meg_wf')

    inputnode = Node(name='inputnode', interface=IdentityInterface(fields=["subject_id", "subjects_dir", "t1ws", "t2ws", "flairs", "fiducials", "reference"]))
    inputnode.inputs.subject_id = subject_data['subject_id']
    inputnode.inputs.subjects_dir = subjects_dir
    inputnode.inputs.t1ws = subject_data['t1ws']
    inputnode.inputs.t2ws = subject_data['t2ws']
    inputnode.inputs.flairs = subject_data['flairs']
    inputnode.inputs.fiducials = subject_data['landmarks']
    inputnode.inputs.reference = subject_data['landmarks_reference']

    inputnode_iter = Node(name='inputnode_iter', interface=IdentityInterface(fields=['session_id', 'raws', 'emptyrooms', 'crosstalks', 'calibrations']))
    inputnode_iter.iterables = [
        ('session_id', subject_data['sessions_id']),
        ('raws', subject_data['sessions_raws']),
        ('emptyrooms', subject_data['sessions_emptyrooms']),
        ('crosstalks', subject_data['sessions_crosstalks']),
        ('calibrations', subject_data['sessions_calibrations'])
    ]
    inputnode_iter.synchronize = True

    # Config
    confignode = Node(name='confignode', interface=IdentityInterface(fields=['conductivity', 'ico', 'spacing', 'add_dist', 'surface', 'pos', 'mri', 'volume_label']))
    confignode.inputs.conductivity = [0.3]
    confignode.inputs.ico = 4
    confignode.inputs.spacing = 'oct6'
    confignode.inputs.add_dist = False
    confignode.inputs.surface = 'white'
    confignode.inputs.pos = pos
    confignode.inputs.mri = None
    confignode.inputs.volume_label = ['Left-Cerebral-Cortex', 'Left-Cerebellum-Cortex', 'Left-Thalamus', 'Left-Thalamus-Proper', 'Left-Putamen', 'Left-Pallidum', 'Left-Hippocampus', 'Left-Amygdala', 'Left-Accumbens-area',
                                      'Right-Cerebral-Cortex', 'Right-Cerebellum-Cortex', 'Right-Thalamus', 'Right-Thalamus-Proper', 'Right-Putamen', 'Right-Pallidum', 'Right-Hippocampus', 'Right-Amygdala', 'Right-Accumbens-area']

    # Anat
    anat_preproc_wf =  init_anat_preproc_wf(bids_root=bids_root,
                                    output_dir='smriprep',
                                    freesurfer=True,
                                    hires=True,
                                    longitudinal=False,
                                    msm_sulc=True,
                                    t1w=subject_data['t1ws'],
                                    t2w=subject_data['t2ws'],
                                    flair=subject_data['flairs'],
                                    skull_strip_mode='force',
                                    skull_strip_template=Reference('OASIS30ANTs'),
                                    spaces=spaces,
                                    precomputed={},
                                    omp_nthreads=1)
    wf.connect(inputnode, 'subject_id', anat_preproc_wf , 'inputnode.subject_id')
    wf.connect(inputnode, 'subjects_dir', anat_preproc_wf , 'inputnode.subjects_dir')
    wf.connect(inputnode, 't1ws', anat_preproc_wf , 'inputnode.t1w')
    if subject_data['t2ws']:
        wf.connect(inputnode, 't2ws', anat_preproc_wf , 'inputnode.t2w')
    if subject_data['flairs']:
        wf.connect(inputnode, 'flairs', anat_preproc_wf , 'inputnode.flair')

    # fiducials
    fiducials_wf = init_fiducials_wf(name="meg_fiducials_wf", work_dir=None)
    wf.connect(inputnode, 'fiducials', fiducials_wf, 'inputnode.fiducials')
    wf.connect(inputnode, 'reference', fiducials_wf, 'inputnode.reference')
    wf.connect(anat_preproc_wf, 'outputnode.subject_id', fiducials_wf, 'inputnode.subject_id')
    wf.connect(anat_preproc_wf, 'outputnode.subjects_dir', fiducials_wf, 'inputnode.subjects_dir')

    # MEG anat
    meg_anat_wf = init_meg_anat_wf(volume_src=volume_src, surface_src=surface_src, name="meg_anat_wf")
    wf.connect(anat_preproc_wf, 'outputnode.subject_id', meg_anat_wf, 'inputnode.subject_id')
    wf.connect(anat_preproc_wf, 'outputnode.subjects_dir', meg_anat_wf, 'inputnode.subjects_dir')
    wf.connect(confignode, 'conductivity', meg_anat_wf, 'inputnode.conductivity')
    wf.connect(confignode, 'ico', meg_anat_wf, 'inputnode.ico')
    wf.connect(confignode, 'spacing', meg_anat_wf, 'inputnode.spacing')
    wf.connect(confignode, 'add_dist', meg_anat_wf, 'inputnode.add_dist')
    wf.connect(confignode, 'surface', meg_anat_wf, 'inputnode.surface')
    wf.connect(confignode, 'pos', meg_anat_wf, 'inputnode.pos')
    wf.connect(confignode, 'mri', meg_anat_wf, 'inputnode.mri')
    wf.connect(confignode, 'volume_label', meg_anat_wf, 'inputnode.volume_label')

    # Maxwell
    meg_maxwell_wf = init_maxwell_wf(name="meg_maxwell_wf")
    wf.connect(inputnode_iter, 'raws', meg_maxwell_wf, 'inputnode.raws')
    wf.connect(inputnode_iter, 'emptyrooms', meg_maxwell_wf, 'inputnode.emptyrooms')
    wf.connect(inputnode_iter, 'crosstalks', meg_maxwell_wf, 'inputnode.crosstalks')
    wf.connect(inputnode_iter, 'calibrations', meg_maxwell_wf, 'inputnode.calibrations')

    # Forward model
    make_coreg = Node(MakeCoreg(), name="make_coreg")
    make_coreg.inputs.distance = 0.005
    make_coreg.inputs.fname = 'trans.fif'
    make_coreg.inputs.overwrite = True

    wf.connect(meg_maxwell_wf, 'outputnode.info', make_coreg, 'info')
    wf.connect(fiducials_wf, 'outputnode.fiducials', make_coreg, 'fiducials')
    wf.connect(meg_anat_wf, 'outputnode.subject_id', make_coreg, 'subject')
    wf.connect(meg_anat_wf, 'outputnode.subjects_dir', make_coreg, 'subjects_dir')

    make_forward_solution = Node(MakeForwardSolution(), name="make_forward_solution")
    make_forward_solution.inputs.fname = 'forward.fif'
    make_forward_solution.inputs.overwrite = True
    wf.connect(meg_maxwell_wf, 'outputnode.info', make_forward_solution, 'info')
    wf.connect(meg_anat_wf, 'outputnode.bem', make_forward_solution, 'bem')
    wf.connect(meg_anat_wf, 'outputnode.src', make_forward_solution, 'src')
    wf.connect(make_coreg, 'trans', make_forward_solution, 'trans')

    # Report
    make_report = Node(MakeReport(), name="make_report")
    make_report.inputs.fname = 'report'
    wf.connect(inputnode, 'subject_id', make_report, 'subject')
    wf.connect(inputnode, 'subjects_dir', make_report, 'subjects_dir')
    wf.connect(meg_maxwell_wf, 'outputnode.raw_tsss', make_report, 'raws')
    wf.connect(meg_maxwell_wf, 'outputnode.head_positions', make_report, 'head_positions')
    wf.connect(meg_maxwell_wf, 'outputnode.info', make_report, 'info')
    wf.connect(make_coreg, 'trans', make_report, 'trans')
    wf.connect(make_forward_solution, 'forward', make_report, 'forward')

    # DataSinks
    datasink_session = Node(DataSink(base_directory=subject_dir, parameterization=False), name='datasink_session')
    wf.connect(inputnode_iter, 'session_id', datasink_session, 'container')
    wf.connect(meg_maxwell_wf, 'outputnode.destination', datasink_session, 'meg.@destination')
    wf.connect(meg_maxwell_wf, 'outputnode.raw_tsss', datasink_session, 'meg.@raw_tsss')
    wf.connect(meg_maxwell_wf, 'outputnode.raw_tsss_splits', datasink_session, 'meg.@splits')
    wf.connect(meg_maxwell_wf, 'outputnode.emptyroom_tsss', datasink_session, 'meg.@emptyroom_tsss')
    wf.connect(meg_maxwell_wf, 'outputnode.emptyroom_tsss_splits', datasink_session, 'meg.@emptyroom_tsss_splits')
    wf.connect(make_forward_solution, 'forward', datasink_session, 'meg.@forward')
    wf.connect(make_report, 'html_report', datasink_session, 'meg.@report_html')

    datasink_anat = Node(DataSink(base_directory=subject_dir, parameterization=False), name='datasink_anat')
    wf.connect(anat_preproc_wf, 'outputnode.t1w_preproc', datasink_anat, 'anat.@t1w_preproc')
    wf.connect(anat_preproc_wf, 'outputnode.t1w_mask', datasink_anat, 'anat.@t1w_mask')
    wf.connect(anat_preproc_wf, 'outputnode.anat2std_xfm', datasink_anat, 'anat.@anat2std_xfm')
    wf.connect(anat_preproc_wf, 'outputnode.std2anat_xfm', datasink_anat, 'anat.@std2anat_xfm')
    wf.connect(anat_preproc_wf, 'outputnode.fsnative2t1w_xfm', datasink_anat, 'anat.@fsnative2t1w_xfm')
    return wf
