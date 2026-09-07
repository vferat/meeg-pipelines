import nipype.pipeline.engine as pe
from nipype import Node, Workflow

from nipype.interfaces.utility import Merge, IdentityInterface, Function

from ...workflows.anat.bem import generate_bem_workflow

from ...interfaces.mne import (
    SetupForwardModel,
    SetupSurfaceSourceSpace,
    SetupVolumeSourceSpace,
    CombineSourceSpaces,
    MakeHeadSurface,
)


def _generate_filenames(subject, subjects_dir):
    forward_model_fname = f"{subject}-bem.fif"
    surfsrc_fname = f"{subject}_src-surface-src.fif"
    volsrc_name = f"{subject}_src-vol-src.fif"
    combinedsrc_name = f"{subject}-src-combined-src.fif"

    return (
        forward_model_fname,
        surfsrc_fname,
        volsrc_name,
        combinedsrc_name,
    )



def init_meg_anat_wf(
    name="meg_anat_workflow",
    surface_src=True,
    volume_src=True,
    work_dir=None):
    # Initiate workflow
    wf = Workflow(name=name, base_dir=work_dir)

    # Nodes
    ## Inputs
    inputnode = Node(
        IdentityInterface(
            fields=[
                "subject_id",
                "subjects_dir",
                "ico",
                "conductivity",
                "add_dist",
                "spacing",
                "surface",
                "pos",
                "mri",
                "volume_label",
                "overwrite",
                "verbose",
            ],
            mandatory_inputs=True,
        ),
        name="inputnode",
    )
    inputnode.inputs.overwrite = True

    ### Generate file names
    generate_filenames = pe.Node(
        name="generate_filenames",
        interface=Function(
            input_names=["subject", "subjects_dir"],
            output_names=[
                "forward_model_fname",
                "surfsrc_fname",
                "volsrc_name",
                "combinedsrc_name",
            ],
            function=_generate_filenames,
        ),
    )
    ### Watershed BEM
    watershed_bem = generate_bem_workflow(name="watershed_bem_workflow")

    ### Setup forward
    setup_forward_model = Node(SetupForwardModel(), name="setup_forward_model")

    ### Combine Sources
    merge_sources = Node(Merge(2), name="merge_sources")
    combine_source_spaces = Node(CombineSourceSpaces(), name="combine_source_spaces")

    ### Make head surface
    make_head_surface = Node(MakeHeadSurface(), name="make_head_surface")

    ### output
    outputnode = Node(
        interface=IdentityInterface(fields=["bem", "src", "subject_id", "subjects_dir"]),
        name="outputnode",
    )

    ### Source spaces
    #### Setup source space (surface)
    if surface_src:
        setup_surface_source_space = Node(
            SetupSurfaceSourceSpace(), name="setup_surface_source_space"
        )
        setup_surface_source_space.inputs.n_jobs = 1

        wf.connect([(inputnode, setup_surface_source_space, [("surface", "surface")])])
        wf.connect([(inputnode, setup_surface_source_space, [("spacing", "spacing")])])
        wf.connect(
            [(inputnode, setup_surface_source_space, [("add_dist", "add_dist")])]
        )
        wf.connect(
            [(inputnode, setup_surface_source_space, [("overwrite", "overwrite")])]
        )
        wf.connect([(inputnode, setup_surface_source_space, [("verbose", "verbose")])])
        wf.connect(
            [
                (
                    generate_filenames,
                    setup_surface_source_space,
                    [("surfsrc_fname", "fname")],
                )
            ]
        )
        wf.connect(
            [(watershed_bem, setup_surface_source_space, [("outputnode.subject_id", "subject")])]
        )
        wf.connect(
            [
                (
                    watershed_bem,
                    setup_surface_source_space,
                    [("outputnode.subjects_dir", "subjects_dir")],
                )
            ]
        )
        if not volume_src:
            wf.connect(
                [(setup_surface_source_space, outputnode, [("src", "src")])]
            )

    #### Setup source space (volume)
    if volume_src:
        setup_volume_source_space = Node(
            SetupVolumeSourceSpace(), name="setup_volume_source_space"
        )
        setup_volume_source_space.inputs.single_volume = True

        wf.connect([(inputnode, setup_volume_source_space, [("pos", "pos")])])
        wf.connect([(inputnode, setup_volume_source_space, [("mri", "mri")])])
        wf.connect(
            [(inputnode, setup_volume_source_space, [("volume_label", "volume_label")])]
        )
        wf.connect(
            [(inputnode, setup_volume_source_space, [("overwrite", "overwrite")])]
        )
        wf.connect(
            [
                (
                    generate_filenames,
                    setup_volume_source_space,
                    [("volsrc_name", "fname")],
                )
            ]
        )
        wf.connect(
            [(watershed_bem, setup_volume_source_space, [("outputnode.subject_id", "subject")])]
        )
        wf.connect(
            [
                (
                    watershed_bem,
                    setup_volume_source_space,
                    [("outputnode.subjects_dir", "subjects_dir")],
                )
            ]
        )
        wf.connect(
            [
                (
                    setup_forward_model,
                    setup_volume_source_space,
                    [("bem_surfaces", "bem")],
                )
            ]
        )

        if not surface_src:
            wf.connect(
                [(setup_volume_source_space, outputnode, [("src", "src")])]
            )

    if volume_src and surface_src:
        wf.connect([(setup_surface_source_space, merge_sources, [("src", "in1")])])
        wf.connect([(setup_volume_source_space, merge_sources, [("src", "in2")])])
        wf.connect(
            [
                (
                    generate_filenames,
                    combine_source_spaces,
                    [("combinedsrc_name", "fname")],
                )
            ]
        )
        wf.connect([(merge_sources, combine_source_spaces, [("out", "sources")])])
        wf.connect([(combine_source_spaces, outputnode, [("src", "src")])])

    ### Connections
    wf.connect([(inputnode, generate_filenames, [("subject_id", "subject")])])
    wf.connect([(inputnode, generate_filenames, [("subjects_dir", "subjects_dir")])])

    wf.connect([(inputnode, watershed_bem, [("subject_id", "inputnode.subject_id")])])
    wf.connect([(inputnode, watershed_bem, [("subjects_dir", "inputnode.subjects_dir")])])

    wf.connect([(inputnode, setup_forward_model, [("ico", "ico")])])
    wf.connect([(inputnode, setup_forward_model, [("conductivity", "conductivity")])])
    wf.connect([(inputnode, setup_forward_model, [("overwrite", "overwrite")])])
    wf.connect([(inputnode, setup_forward_model, [("verbose", "verbose")])])
    wf.connect(
        [(generate_filenames, setup_forward_model, [("forward_model_fname", "fname")])]
    )
    wf.connect([(watershed_bem, setup_forward_model, [("outputnode.subject_id", "subject")])])
    wf.connect(
        [(watershed_bem, setup_forward_model, [("outputnode.subjects_dir", "subjects_dir")])]
    )

    wf.connect([(watershed_bem, make_head_surface, [("outputnode.subject_id", "subject")])])
    wf.connect([(watershed_bem, make_head_surface, [("outputnode.subjects_dir", "subjects_dir")])])

    wf.connect([(inputnode, make_head_surface, [("verbose", "verbose")])])
    wf.connect([(inputnode, make_head_surface, [("overwrite", "overwrite")])])

    ## output
    wf.connect(setup_forward_model, "bem_solution", outputnode, "bem")
    wf.connect(make_head_surface, "subject", outputnode, "subject_id")
    wf.connect(make_head_surface, "subjects_dir", outputnode, "subjects_dir")
    return wf
