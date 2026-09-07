import os

import nipype.pipeline.engine as pe
from nipype import Node


from  nipype.interfaces.io import FreeSurferSource, DataSink
from nipype.interfaces.utility import Function, IdentityInterface, Rename
from nipype.interfaces.fsl.maths import ApplyMask
from nipype.interfaces.freesurfer.preprocess import MRIConvert

from ..meegpype.interfaces.freesurfer.mri_watershed import MRIWatershed


def generate_bem_path(subject_id, subjects_dir):
    import os
    return os.path.join(subjects_dir, subject_id, 'bem')

def generate_fs_bem_workflow(
        subject_id=None,
        subjects_dir=None,
        brainmask=None,
        name="freesurfer_bem_surfaces"):
    
    # Initilaze workflow
    wf = pe.Workflow(name=name)

    inputnode = Node(IdentityInterface(fields=['subject_id', 'subjects_dir', 'brainmask']), name='inputnode')
    inputnode.inputs.subject_id = subject_id
    inputnode.inputs.subjects_dir = subjects_dir
    inputnode.inputs.brainmask = brainmask

    # FS source
    fs_source = Node(FreeSurferSource(), name='fs_source')

    # convert t1w to nii
    mri_convert = Node(MRIConvert(), name='mri_convert')
    mri_convert.inputs.out_type = 'niigz'

    # Apply brainmask to T1w
    apply_mask = Node(ApplyMask(), name='apply_mask')
    apply_mask.inputs.out_file = 'brain.nii.gz'

    # Brain and inner skull surfaces
    watershed_brain = Node(MRIWatershed(), name='watershed_brain')
    watershed_brain.inputs.n = True
    watershed_brain.inputs.T1 = True
    watershed_brain.inputs.outvol = "brain_watershed.mgz"
    watershed_brain.inputs.surf = 'watershed_brain'
    watershed_brain.inputs.useSRAS = True

    # Other surfaces
    watershed_skull = Node(MRIWatershed(), name='watershed_skull')
    watershed_brain.inputs.T1 = True
    watershed_skull.inputs.outvol = "watershed.mgz"
    watershed_skull.inputs.surf = 'watershed_skull'
    watershed_skull.inputs.useSRAS = True

    # rename files
    rename_brain_surf = Node(Rename(format_string='brain.surf'), name='rename_brain_surf')
    rename_inner_skull_surf = Node(Rename(format_string='inner_skull.surf'), name='rename_inner_skull_surf')
    rename_outer_skull_surf = Node(Rename(format_string='outer_skull.surf'), name='rename_outer_skull_surf')
    rename_outer_skin_surf = Node(Rename(format_string='outer_skin.surf'), name='rename_outer_skin_surf')

    # create BEM path
    create_bem_path = Node(Function(input_names=['subject_id', 'subjects_dir'],
                                    output_names=['bem_path'],
                                    function=generate_bem_path),
                           name='create_bem_path')
    
    # Create BEM folder
    datasink = Node(DataSink(), name='datasink')


    ## Connections
    wf.connect(inputnode, 'subject_id', fs_source, 'subject_id')
    wf.connect(inputnode, 'subjects_dir', fs_source, 'subjects_dir')
    wf.connect(inputnode, 'subject_id', create_bem_path, 'subject_id')
    wf.connect(inputnode, 'subjects_dir', create_bem_path, 'subjects_dir')
    wf.connect(inputnode, 'brainmask', apply_mask, 'mask_file')

    wf.connect(fs_source, 'T1', mri_convert, 'in_file')
    wf.connect(mri_convert, 'out_file', apply_mask, 'in_file')

    wf.connect(apply_mask, 'out_file', watershed_brain, 'invol')

    wf.connect(fs_source, 'T1', watershed_skull, 'invol')


    wf.connect(watershed_brain, 'surf_brain_surface', rename_brain_surf, 'in_file')
    wf.connect(watershed_brain, 'surf_inner_skull_surface', rename_inner_skull_surf, 'in_file')

    wf.connect(watershed_skull, 'surf_outer_skull_surface', rename_outer_skull_surf, 'in_file')
    wf.connect(watershed_skull, 'surf_outer_skin_surface', rename_outer_skin_surf, 'in_file')

    wf.connect(create_bem_path, 'bem_path', datasink, 'base_directory')
    wf.connect(rename_brain_surf, 'out_file', datasink, 'surface.@brain_surf')
    wf.connect(rename_inner_skull_surf, 'out_file', datasink, 'surface.@inner_skull_surf')
    wf.connect(rename_outer_skull_surf, 'out_file', datasink, 'surface.@outer_skull_surf')
    wf.connect(rename_outer_skin_surf, 'out_file', datasink, 'surface.@outer_skin_surf')

    ## output
    outputnode = Node(
        interface=IdentityInterface(fields=["subject_id", "subjects_dir", 'out_file']), name="outputnode"
    )
    wf.connect(inputnode, 'subject_id', outputnode, 'subject_id')
    wf.connect(inputnode, 'subjects_dir', outputnode, 'subjects_dir')
    wf.connect(datasink, 'out_file', outputnode, 'out_file')



    return wf