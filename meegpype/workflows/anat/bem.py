import nipype.pipeline.engine as pe
from nipype import Node

from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import FreeSurferSource, DataSink
from nipype.interfaces.freesurfer import MRIsExpand, MRIConvert

from niworkflows.interfaces.freesurfer import RefineBrainMask

from ...interfaces.freesurfer.mri_mc import MRImc
from ...interfaces.freesurfer.mris_smooth import MRIsSmooth
from ...interfaces.freesurfer.mri_binarize import MRIBinarize
from ...interfaces.mne.decimate_surface import DecimateSurface
from ...interfaces.mne.bem import MakeWatershedBEM


def generate_bem_workflow(
        subject_id=None,
        subjects_dir=None,
        name="freesurfer_bem_surfaces",
        default=True):

    # utils
    def generate_subject_dir_path(subjects_dir, subject_id):
        import os
        return os.path.abspath(os.path.join(subjects_dir, subject_id))

    # Initilaze workflow
    wf = pe.Workflow(name=name)

    inputnode = Node(IdentityInterface(fields=['subject_id', 'subjects_dir']), name='inputnode')
    inputnode.inputs.subject_id = subject_id
    inputnode.inputs.subjects_dir = subjects_dir

    outputnode = Node(
        interface=IdentityInterface(fields=["subject_id", "subjects_dir", "brain_surf", 'inner_skull_surf']), name="outputnode"
    )
    
    if default:
        watershed = Node(MakeWatershedBEM(), name='watershed')
        watershed.inputs.overwrite = True

        wf.connect(inputnode, 'subject_id', watershed, 'subject')
        wf.connect(inputnode, 'subjects_dir', watershed, 'subjects_dir')

        wf.connect(watershed, 'subject', outputnode, 'subject_id')
        wf.connect(watershed, 'subjects_dir', outputnode, 'subjects_dir')
        wf.connect(watershed, 'brain_surf', outputnode, 'brain_surf')
        wf.connect(watershed, 'inner_skull', outputnode, 'inner_skull_surf')

    else:    
        fs_source = Node(FreeSurferSource(), name='fs_source')
        fs_source.hemi = 'both'

        convert_aseg = Node(MRIConvert(), name='convert_aseg')
        convert_aseg.inputs.out_type = 'niigz'

        convert_t1 = Node(MRIConvert(), name='convert_t1')
        convert_t1.inputs.out_type = 'niigz'

        convert_brain = Node(MRIConvert(), name='convert_brain')
        convert_brain.inputs.out_type = 'niigz'

        refine_brain_mask = Node(RefineBrainMask(), name='refine_brain_mask')

        watershed = Node(MakeWatershedBEM(), name='watershed')
        watershed.inputs.overwrite = True

        mri_binarize = Node(MRIBinarize(), name='mri_binarize')
        mri_binarize.inputs.output_volume = 'brainmask.mgz'
        mri_binarize.inputs.match = 0
        mri_binarize.inputs.inv = True

        mri_mc = Node(MRImc(), name='mri_mc')
        mri_mc.inputs.label_value = 1
        mri_mc.inputs.output_surface = 'brain_mc.surf'

        mris_smooth = Node(MRIsSmooth(), name='mris_smooth')
        mris_smooth.inputs.output_surface = 'brain_mc_smooth.surf'
        mris_smooth.inputs.average = 100
        mris_smooth.inputs.n_iteration = 100

        sync_outputs = Node(IdentityInterface(fields=['watershed_input', 'output_surface']), name='sync_outputs')

        decimate_surface = Node(DecimateSurface(), name='decimate_surface')
        decimate_surface.inputs.n_triangles = 5120
        decimate_surface.inputs.method = 'sphere'
        decimate_surface.inputs.output_surface = 'brain_mc_decimated.surf'

        mris_expand_brain = Node(MRIsExpand(), name='mris_expand_brain')
        mris_expand_brain.inputs.distance = 4
        mris_expand_brain.inputs.out_name = 'brain.surf'

        mris_expand_inner_skull = Node(MRIsExpand(), name='mris_expand_inner_skull')
        mris_expand_inner_skull.inputs.distance = 6
        mris_expand_inner_skull.inputs.out_name = 'inner_skull.surf'
        mris_expand_inner_skull.inputs.smooth_averages = 10

        generate_bem_path = pe.Node(
            Function(
                input_names=['subjects_dir', 'subject_id'],
                output_names=['subject_dir'],
                function=generate_subject_dir_path,
            ),
            name='generate_bem_path',
        )

        datasink_brain_surf = Node(DataSink(), name='datasink_brain_surf')
        datasink_inner_skull_surf = Node(DataSink(), name='datasink_inner_skull_surf')
        datasink_brain_vol = Node(DataSink(), name='datasink_brain_vol')

        ## Connections
        wf.connect(inputnode, 'subject_id', fs_source, 'subject_id')
        wf.connect(inputnode, 'subjects_dir', fs_source, 'subjects_dir')

        wf.connect(fs_source, 'aseg', convert_aseg, 'in_file')
        wf.connect(fs_source, 'T1', convert_t1, 'in_file')
        wf.connect(fs_source, 'brain', convert_brain, 'in_file')

        wf.connect(convert_t1, 'out_file', refine_brain_mask, 'in_anat')
        wf.connect(convert_brain, 'out_file', refine_brain_mask, 'in_ants')
        wf.connect(convert_aseg, 'out_file', refine_brain_mask, 'in_aseg')

        wf.connect(inputnode, 'subject_id', watershed, 'subject')
        wf.connect(inputnode, 'subjects_dir', watershed, 'subjects_dir')

        wf.connect(inputnode, 'subjects_dir', generate_bem_path, 'subjects_dir')
        wf.connect(inputnode, 'subject_id', generate_bem_path, 'subject_id')

        wf.connect(generate_bem_path, 'subject_dir', datasink_brain_surf, 'base_directory')
        wf.connect(generate_bem_path, 'subject_dir', datasink_inner_skull_surf, 'base_directory')

        wf.connect(refine_brain_mask, 'out_file', mri_binarize, 'input_volume')

        wf.connect(mri_binarize, 'output_volume', mri_mc, 'input_volume')
        wf.connect(mri_mc, 'output_surface', mris_smooth, 'input_surface')

        wf.connect(mris_smooth, 'output_surface', decimate_surface, 'input_surface')

        # Sync mri_expand_brain with watershed to ensure that mri_expand_brain overwrites the watershed output surfaces
        wf.connect(watershed, 'subject', sync_outputs, 'watershed_input')
        wf.connect(decimate_surface, 'output_surface', sync_outputs, 'output_surface')

        wf.connect(sync_outputs, 'output_surface', mris_expand_brain, 'in_file')
        wf.connect(mris_expand_brain, 'out_file', mris_expand_inner_skull, 'in_file')

        wf.connect(mris_expand_brain, 'out_file', datasink_brain_surf, 'bem.@brain_surf')
        wf.connect(mris_expand_inner_skull, 'out_file', datasink_inner_skull_surf, 'bem.@inner_skull_surf')

        wf.connect(refine_brain_mask, 'out_file', datasink_brain_vol, 'bem.@brain_vol')
        wf.connect(generate_bem_path, 'subject_dir', datasink_brain_vol, 'base_directory')

        wf.connect(watershed, 'subject', outputnode, 'subject_id')
        wf.connect(watershed, 'subjects_dir', outputnode, 'subjects_dir')
        wf.connect(datasink_brain_surf, 'out_file', outputnode, 'brain_surf')
        wf.connect(datasink_inner_skull_surf, 'out_file', outputnode, 'inner_skull_surf')

    return wf
