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


def install_bem_surfaces(subjects_dir, subject, brain, inner_skull, outer_skull, outer_skin):
    """Install the BEM surfaces in subjects_dir/subject/bem.

    Existing files are only replaced when their content differs, so that unchanged
    surfaces keep their timestamps (and nipype caches).
    """
    import os
    import filecmp
    import shutil

    bem_dir = os.path.join(subjects_dir, subject, "bem")
    sources = {
        "brain": brain,
        "inner_skull": inner_skull,
        "outer_skull": outer_skull,
        "outer_skin": outer_skin,
    }
    installed = {}
    for name, source in sources.items():
        destination = os.path.join(bem_dir, f"{name}.surf")
        # Never write through a symlink: it would modify the file it points to.
        if (
            os.path.islink(destination)
            or not os.path.exists(destination)
            or not filecmp.cmp(source, destination, shallow=False)
        ):
            if os.path.lexists(destination):
                os.remove(destination)
            shutil.copyfile(source, destination)
        installed[name] = destination

    return (
        subject,
        subjects_dir,
        installed["brain"],
        installed["inner_skull"],
        installed["outer_skull"],
        installed["outer_skin"],
    )


def generate_bem_workflow(
        subject_id=None,
        subjects_dir=None,
        name="freesurfer_bem_surfaces",
        method="basic"):

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
        interface=IdentityInterface(fields=["subject_id", "subjects_dir", "brain_surf", "inner_skull_surf", "outer_skull_surf", "outer_skin_surf"]), name="outputnode"
    )

    # The bem folder is shared between methods and modified by previous runs, so the
    # surfaces of the current method are reinstalled on every run (even when cached).
    install_surfaces = Node(
        Function(
            input_names=['subjects_dir', 'subject', 'brain', 'inner_skull', 'outer_skull', 'outer_skin'],
            output_names=['subject', 'subjects_dir', 'brain_surf', 'inner_skull_surf', 'outer_skull_surf', 'outer_skin_surf'],
            function=install_bem_surfaces,
        ),
        name='install_surfaces',
        overwrite=True,
    )

    wf.connect(install_surfaces, 'subject', outputnode, 'subject_id')
    wf.connect(install_surfaces, 'subjects_dir', outputnode, 'subjects_dir')
    wf.connect(install_surfaces, 'brain_surf', outputnode, 'brain_surf')
    wf.connect(install_surfaces, 'inner_skull_surf', outputnode, 'inner_skull_surf')
    wf.connect(install_surfaces, 'outer_skull_surf', outputnode, 'outer_skull_surf')
    wf.connect(install_surfaces, 'outer_skin_surf', outputnode, 'outer_skin_surf')

    if method == "basic":
        watershed = Node(MakeWatershedBEM(), name='watershed')
        watershed.inputs.overwrite = True

        wf.connect(inputnode, 'subject_id', watershed, 'subject')
        wf.connect(inputnode, 'subjects_dir', watershed, 'subjects_dir')

        # All surfaces from watershed
        wf.connect(watershed, 'subject', install_surfaces, 'subject')
        wf.connect(watershed, 'subjects_dir', install_surfaces, 'subjects_dir')
        wf.connect(watershed, 'watershed_brain_surf', install_surfaces, 'brain')
        wf.connect(watershed, 'watershed_inner_skull', install_surfaces, 'inner_skull')
        wf.connect(watershed, 'watershed_outer_skull', install_surfaces, 'outer_skull')
        wf.connect(watershed, 'watershed_outer_skin', install_surfaces, 'outer_skin')

    elif method == "refined":
        fs_source = Node(FreeSurferSource(), name='fs_source')
        fs_source.inputs.hemi = 'both'

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

        decimate_surface = Node(DecimateSurface(), name='decimate_surface')
        decimate_surface.inputs.n_triangles = 5120
        decimate_surface.inputs.method = 'sphere'
        decimate_surface.inputs.output_surface = 'brain_mc_decimated.surf'

        mris_expand_brain = Node(MRIsExpand(), name='mris_expand_brain')
        mris_expand_brain.inputs.distance = 1
        mris_expand_brain.inputs.out_name = 'brain.surf'

        mris_expand_inner_skull = Node(MRIsExpand(), name='mris_expand_inner_skull')
        mris_expand_inner_skull.inputs.distance = 3
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

        wf.connect(refine_brain_mask, 'out_file', mri_binarize, 'input_volume')

        wf.connect(mri_binarize, 'output_volume', mri_mc, 'input_volume')
        wf.connect(mri_mc, 'output_surface', mris_smooth, 'input_surface')

        wf.connect(mris_smooth, 'output_surface', decimate_surface, 'input_surface')

        wf.connect(decimate_surface, 'output_surface', mris_expand_brain, 'in_file')
        wf.connect(mris_expand_brain, 'out_file', mris_expand_inner_skull, 'in_file')

        wf.connect(refine_brain_mask, 'out_file', datasink_brain_vol, 'bem.@brain_vol')
        wf.connect(generate_bem_path, 'subject_dir', datasink_brain_vol, 'base_directory')

        # Refined brain and inner skull, outer skull and skin from watershed
        wf.connect(watershed, 'subject', install_surfaces, 'subject')
        wf.connect(watershed, 'subjects_dir', install_surfaces, 'subjects_dir')
        wf.connect(mris_expand_brain, 'out_file', install_surfaces, 'brain')
        wf.connect(mris_expand_inner_skull, 'out_file', install_surfaces, 'inner_skull')
        wf.connect(watershed, 'watershed_outer_skull', install_surfaces, 'outer_skull')
        wf.connect(watershed, 'watershed_outer_skin', install_surfaces, 'outer_skin')

    else:
        raise ValueError(f"Unknown method: {method}")
    return wf
