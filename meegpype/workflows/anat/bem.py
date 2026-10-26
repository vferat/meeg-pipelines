"""BEM surface workflows.

All workflows write their surfaces to ``subjects_dir/subject_id/bem`` (``brain.surf``,
``inner_skull.surf``, ``outer_skull.surf`` and ``outer_skin.surf``), the location MNE
reads them from. Since this folder is shared between methods, the surfaces of the
current workflow are reinstalled on every run, even when nodes are cached: the content
of the ``bem`` folder always matches the workflow that ran last.
"""

import nipype.pipeline.engine as pe
from nipype import Node

from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import FreeSurferSource
from nipype.interfaces.freesurfer import MRIsExpand

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


def _init_bem_workflow(name, subject_id, subjects_dir):
    """Create the workflow, its input/output nodes and the surface installation node."""
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

    return wf, inputnode, install_surfaces


def generate_basic_bem_workflow(
        subject_id=None,
        subjects_dir=None,
        name="basic_bem_workflow"):
    """Build the basic BEM workflow, using the watershed algorithm.

    All BEM surfaces (brain, inner skull, outer skull and outer skin) are computed
    with :func:`mne.bem.make_watershed_bem` and installed in
    ``subjects_dir/subject_id/bem``.

    Workflow Graph
        .. workflow::
            :graph2use: orig
            :simple_form: yes

            from meegpype.workflows.anat.bem import generate_basic_bem_workflow
            wf = generate_basic_bem_workflow()

    Parameters
    ----------
    subject_id : str, optional
        FreeSurfer subject ID. Can also be connected to ``inputnode.subject_id``.
    subjects_dir : str, optional
        FreeSurfer subjects directory. Can also be connected to
        ``inputnode.subjects_dir``.
    name : str
        Name of the workflow.

    Notes
    -----
    The ``outputnode`` provides ``subject_id``, ``subjects_dir`` and the paths of the
    installed surfaces: ``brain_surf``, ``inner_skull_surf``, ``outer_skull_surf`` and
    ``outer_skin_surf``.
    """
    wf, inputnode, install_surfaces = _init_bem_workflow(name, subject_id, subjects_dir)

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

    return wf


def generate_refined_bem_workflow(
        subject_id=None,
        subjects_dir=None,
        inner_skull_distance=2,
        name="refined_bem_workflow"):
    """Build the refined BEM workflow, using the FreeSurfer brain mask.

    The brain and inner skull surfaces are computed from the FreeSurfer
    ``brainmask.mgz``. In the forward pipeline, it holds the ANTs brain extraction
    computed by sMRIPrep (FreeSurfer's own skull stripping is skipped), which
    includes the CSF surrounding the brain:

    1. the mask is binarized;
    2. a surface is extracted with marching cubes (``mri_mc``), smoothed and
       decimated to 5120 triangles;
    3. the brain surface is obtained by expanding it by 1 mm, and the inner skull
       surface by expanding the brain surface by a further ``inner_skull_distance``
       mm (2 mm by default).

    The outer skull and outer skin surfaces are computed with
    :func:`mne.bem.make_watershed_bem`. All surfaces are installed in
    ``subjects_dir/subject_id/bem``.

    Workflow Graph
        .. workflow::
            :graph2use: orig
            :simple_form: yes

            from meegpype.workflows.anat.bem import generate_refined_bem_workflow
            wf = generate_refined_bem_workflow()

    Parameters
    ----------
    subject_id : str, optional
        FreeSurfer subject ID. Can also be connected to ``inputnode.subject_id``.
    subjects_dir : str, optional
        FreeSurfer subjects directory. Can also be connected to
        ``inputnode.subjects_dir``.
    inner_skull_distance : float
        Distance (in mm) between the brain and the inner skull surfaces.
    name : str
        Name of the workflow.

    Notes
    -----
    The ``outputnode`` provides ``subject_id``, ``subjects_dir`` and the paths of the
    installed surfaces: ``brain_surf``, ``inner_skull_surf``, ``outer_skull_surf`` and
    ``outer_skin_surf``.
    """
    wf, inputnode, install_surfaces = _init_bem_workflow(name, subject_id, subjects_dir)
    fs_source = Node(FreeSurferSource(), name='fs_source')

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
    mris_smooth.inputs.average = 15
    mris_smooth.inputs.n_iteration = 10

    decimate_surface = Node(DecimateSurface(), name='decimate_surface')
    decimate_surface.inputs.n_triangles = 5120
    decimate_surface.inputs.method = 'sphere'
    decimate_surface.inputs.output_surface = 'brain_mc_decimated.surf'

    mris_expand_brain = Node(MRIsExpand(), name='mris_expand_brain')
    mris_expand_brain.inputs.distance = 1
    mris_expand_brain.inputs.out_name = 'brain.surf'

    mris_expand_inner_skull = Node(MRIsExpand(), name='mris_expand_inner_skull')
    mris_expand_inner_skull.inputs.distance = inner_skull_distance
    mris_expand_inner_skull.inputs.out_name = 'inner_skull.surf'
    mris_expand_inner_skull.inputs.smooth_averages = 3

    ## Connections
    wf.connect(inputnode, 'subject_id', watershed, 'subject')
    wf.connect(inputnode, 'subjects_dir', watershed, 'subjects_dir')

    wf.connect(inputnode, 'subject_id', fs_source, 'subject_id')
    wf.connect(inputnode, 'subjects_dir', fs_source, 'subjects_dir')
    wf.connect(fs_source, 'brainmask', mri_binarize, 'input_volume')

    wf.connect(mri_binarize, 'output_volume', mri_mc, 'input_volume')
    wf.connect(mri_mc, 'output_surface', mris_smooth, 'input_surface')

    wf.connect(mris_smooth, 'output_surface', decimate_surface, 'input_surface')

    wf.connect(decimate_surface, 'output_surface', mris_expand_brain, 'in_file')
    wf.connect(mris_expand_brain, 'out_file', mris_expand_inner_skull, 'in_file')

    # Refined brain and inner skull, outer skull and skin from watershed
    wf.connect(watershed, 'subject', install_surfaces, 'subject')
    wf.connect(watershed, 'subjects_dir', install_surfaces, 'subjects_dir')
    wf.connect(mris_expand_brain, 'out_file', install_surfaces, 'brain')
    wf.connect(mris_expand_inner_skull, 'out_file', install_surfaces, 'inner_skull')
    wf.connect(watershed, 'watershed_outer_skull', install_surfaces, 'outer_skull')
    wf.connect(watershed, 'watershed_outer_skin', install_surfaces, 'outer_skin')

    return wf


def generate_bem_workflow(
        subject_id=None,
        subjects_dir=None,
        name="freesurfer_bem_surfaces",
        method="basic",
        inner_skull_distance=None):
    """Build a BEM workflow.

    Parameters
    ----------
    subject_id : str, optional
        FreeSurfer subject ID. Can also be connected to ``inputnode.subject_id``.
    subjects_dir : str, optional
        FreeSurfer subjects directory. Can also be connected to
        ``inputnode.subjects_dir``.
    name : str
        Name of the workflow.
    method : ``"basic"`` | ``"refined"``
        The method used to compute the BEM surfaces, see
        :func:`generate_basic_bem_workflow` and :func:`generate_refined_bem_workflow`.
    inner_skull_distance : float | None
        Distance (in mm) between the brain and the inner skull surfaces, only used by
        the ``"refined"`` method. If None, the default of
        :func:`generate_refined_bem_workflow` is used.
    """
    if method == "basic":
        if inner_skull_distance is not None:
            raise ValueError("inner_skull_distance is only used by the 'refined' method.")
        return generate_basic_bem_workflow(subject_id=subject_id, subjects_dir=subjects_dir, name=name)
    elif method == "refined":
        kwargs = {}
        if inner_skull_distance is not None:
            kwargs["inner_skull_distance"] = inner_skull_distance
        return generate_refined_bem_workflow(subject_id=subject_id, subjects_dir=subjects_dir, name=name, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}")
