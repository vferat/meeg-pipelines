import nipype.pipeline.engine as pe
from nipype import Node

from nipype.interfaces import freesurfer
import nipype.interfaces.io as nio
from nipype.interfaces.utility import Function, Select, IdentityInterface


def generate_fname(atlas_name, subject_id, classifier_data_dir):
    import os
    # classifier
    annot_lh = "lh." + atlas_name + ".annot"
    annot_rh = "rh." + atlas_name + ".annot"
    annot_lh = os.path.join(classifier_data_dir, "fsaverage", "label", annot_lh)
    annot_rh = os.path.join(classifier_data_dir, "fsaverage", "label", annot_rh)
    # Command
    annot_command = "--annot " + atlas_name + "." + subject_id
    # outputs filenames
    label_fname = "sub-" + subject_id + "_seg-" + atlas_name + "_space-fsnative_dseg.nii"
    return (atlas_name, annot_lh, annot_rh, annot_command, label_fname)


def generate_fs_labelling_workflow(
    subject_id=None,
    subjects_dir=None,
    atlas_name=None,
    classifier_data_dir=None,
    name="freesurfer_labelling_workflow",
):
    # Initilaze workflow
    workflow = pe.Workflow(name=name)

    ## Input
    inputnode = Node(
        interface=IdentityInterface(
            fields=["subject_id", "subjects_dir", "atlas_name", "classifier_data_dir"]
        ),
        name="inputnode",
    )
    inputnode.inputs.subject_id = subject_id
    inputnode.inputs.subjects_dir = subjects_dir
    inputnode.inputs.atlas_name = atlas_name
    inputnode.inputs.classifier_data_dir = classifier_data_dir

    source_subject = "fsaverage"

    # Generate annotation file names
    gen_inputs = pe.Node(
        interface=Function(
            input_names=[
                "atlas_name",
                "subject_id",
                "classifier_data_dir",
            ],
            output_names=[
                "atlas_name",
                "annot_lh",
                "annot_rh",
                "annot_command",
                "label_fname",
            ],
            function=generate_fname,
        ),
        name="gen_inputs",
    )

    # processing
    fs_both = pe.Node(interface=nio.FreeSurferSource(), name="fs_both")
    fs_both.inputs.hemi = "both"

    select_ribbon = pe.Node(interface=Select(), name="select_ribbon")
    select_ribbon.inputs.index = [-1]

    fs_rh = pe.Node(interface=nio.FreeSurferSource(), name="fs_rh")
    fs_rh.inputs.hemi = "rh"

    fs_lh = pe.Node(interface=nio.FreeSurferSource(), name="fs_lh")
    fs_lh.inputs.hemi = "lh"

    surface_transform_rh = pe.Node(
        interface=freesurfer.SurfaceTransform(), name="surface_transform_rh"
    )
    surface_transform_rh.inputs.hemi = "rh"
    surface_transform_rh.inputs.source_subject = source_subject

    surface_transform_lh = pe.Node(
        interface=freesurfer.SurfaceTransform(), name="surface_transform_lh"
    )
    surface_transform_lh.inputs.hemi = "lh"
    surface_transform_lh.inputs.source_subject = source_subject

    aparc2aseg = pe.Node(interface=freesurfer.Aparc2Aseg(), name="aparc2aseg")
    aparc2aseg.inputs.label_wm = False
    aparc2aseg.inputs.rip_unknown = True
    aparc2aseg.inputs.copy_inputs = True

    # Workflow
    ## Inputs
    workflow.connect(inputnode, "subject_id", fs_both, "subject_id")
    workflow.connect(inputnode, "subjects_dir", fs_both, "subjects_dir")

    workflow.connect(inputnode, "subject_id", fs_rh, "subject_id")
    workflow.connect(inputnode, "subjects_dir", fs_rh, "subjects_dir")

    workflow.connect(inputnode, "subject_id", fs_lh, "subject_id")
    workflow.connect(inputnode, "subjects_dir", fs_lh, "subjects_dir")

    workflow.connect(inputnode, "subject_id", surface_transform_rh, "target_subject")
    workflow.connect(inputnode, "subjects_dir", surface_transform_rh, "subjects_dir")
    workflow.connect(gen_inputs, "annot_rh", surface_transform_rh, "source_annot_file")

    workflow.connect(inputnode, "subject_id", surface_transform_lh, "target_subject")
    workflow.connect(inputnode, "subjects_dir", surface_transform_lh, "subjects_dir")
    workflow.connect(gen_inputs, "annot_lh", surface_transform_lh, "source_annot_file")

    workflow.connect(inputnode, "subject_id", aparc2aseg, "subject_id")
    workflow.connect(inputnode, "subjects_dir", aparc2aseg, "subjects_dir")

    workflow.connect(inputnode, "atlas_name", gen_inputs, "atlas_name")
    workflow.connect(inputnode, "subject_id", gen_inputs, "subject_id")
    workflow.connect(
        inputnode, "classifier_data_dir", gen_inputs, "classifier_data_dir"
    )

    # Connect Existing files
    workflow.connect(fs_both, "ribbon", select_ribbon, "inlist")

    # aparc2aseg
    workflow.connect(gen_inputs, "annot_command", aparc2aseg, "args")
    workflow.connect(fs_both, "aseg", aparc2aseg, "aseg")
    workflow.connect(select_ribbon, "out", aparc2aseg, "ribbon")
    workflow.connect(fs_rh, "white", aparc2aseg, "rh_white")
    workflow.connect(fs_rh, "pial", aparc2aseg, "rh_pial")
    workflow.connect(fs_rh, "ribbon", aparc2aseg, "rh_ribbon")
    workflow.connect(fs_lh, "white", aparc2aseg, "lh_white")
    workflow.connect(fs_lh, "pial", aparc2aseg, "lh_pial")
    workflow.connect(fs_lh, "ribbon", aparc2aseg, "lh_ribbon")
    workflow.connect(gen_inputs, "label_fname", aparc2aseg, "out_file")
    workflow.connect(surface_transform_lh, "out_file", aparc2aseg, "lh_annotation")
    workflow.connect(surface_transform_rh, "out_file", aparc2aseg, "rh_annotation")

    ## Outputs
    outputnode = Node(
        interface=IdentityInterface(
            fields=[
                "volume",
                "lh_aseg",
                "rh_aseg",
                "atlas_name",
                "subject_id",
                "subjects_dir",
            ]
        ),
        name="outputnode",
    )
    workflow.connect(aparc2aseg, "out_file", outputnode, "volume")
    workflow.connect(inputnode, "subject_id", outputnode, "subject_id")
    workflow.connect(inputnode, "subjects_dir", outputnode, "subjects_dir")
    workflow.connect(gen_inputs, "atlas_name", outputnode, "atlas_name")
    return workflow
