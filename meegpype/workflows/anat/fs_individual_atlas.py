import nipype.pipeline.engine as pe
from nipype import Node

from nipype.interfaces import freesurfer
import nipype.interfaces.io as nio
from nipype.interfaces.utility import Function, Select, IdentityInterface, Rename


def generate_fname(atlas_name, subject_id, subjects_dir, data_dir):
    import os
    from meegpype.data.freesurfer.classifiers import ATLAS
    atlas_dict = next((item for item in ATLAS if item["name"] == atlas_name), None)
    if atlas_dict is None:
        raise ValueError(f"Atlas {atlas_name} not found in ATLAS.")
    else:
        label_fname = f"{subject_id}_space-fsnative_atlas-{atlas_dict['atlas']}"
        if "seg" in atlas_dict:
            label_fname += f"_seg-{atlas_dict['seg']}"
        if "scale" in atlas_dict:
            label_fname += f"_scale-{atlas_dict['scale']}"
        label_fname += "_dseg.nii"

    # classifier
    lh_gcs = "lh." + atlas_name + ".gcs"
    rh_gcs = "rh." + atlas_name + ".gcs"
    lut_name = atlas_name + "_LUT.txt"
    lh_gcs_path = os.path.join(data_dir, "classifiers", lh_gcs)
    rh_gcs_path = os.path.join(data_dir, "classifiers", rh_gcs)
    lut_path = os.path.join(data_dir, "LUTs", lut_name)
    # Command
    annot_command = "--annot " + atlas_name
    # outputs filenames
    lh_fname = "lh." + atlas_name + ".annot"
    lh_fname = os.path.join(subjects_dir, subject_id, "label", lh_fname)
    rh_fname = "rh." + atlas_name + ".annot"
    rh_fname = os.path.join(subjects_dir, subject_id, "label", rh_fname)
    return (
        atlas_name,
        lh_gcs_path,
        rh_gcs_path,
        annot_command,
        lh_fname,
        rh_fname,
        label_fname,
        lut_path,
    )


def _generate_annot_filename(atlas, hemi, subject):
    from meegpype.data.freesurfer.classifiers import ATLAS
    hemi_alias = "R" if hemi == "rh" else "L"

    atlas_dict = next((item for item in ATLAS if item["name"] == atlas), None)
    if atlas_dict is None:
        raise ValueError(f"Atlas {atlas} not found in ATLAS.")
    else:
        subject_annot = f"{subject}_hemi-{hemi_alias}_space-fsnative_atlas-{atlas_dict['atlas']}"
        if "seg" in atlas_dict:
            subject_annot += f"_seg-{atlas_dict['seg']}"
        if "scale" in atlas_dict:
            subject_annot += f"_scale-{atlas_dict['scale']}"
        subject_annot += "_dseg.annot"
    return subject_annot


def generate_fs_labelling_workflow(
    name="freesurfer_labelling_workflow",
    base_dir=None,
):
    # Initilaze workflow
    workflow = pe.Workflow(name=name, base_dir=base_dir)

    ## Input
    inputnode = Node(
        interface=IdentityInterface(
            fields=["subject_id", "subjects_dir", "atlas_name", "data_dir"],
            mandatory_inputs=True,
        ),
        name="inputnode",
    )
    # Generate annotation file names
    gen_inputs = pe.Node(
        interface=Function(
            input_names=[
                "atlas_name",
                "subject_id",
                "subjects_dir",
                "data_dir",
            ],
            output_names=[
                "atlas_name",
                "lh_gcs_path",
                "rh_gcs_path",
                "annot_command",
                "lh_fname",
                "rh_fname",
                "label_fname",
                "lut_path",
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

    ca_label_lh = pe.Node(interface=freesurfer.MRIsCALabel(), name="ca_label_lh")
    ca_label_lh.inputs.hemisphere = "lh"

    ca_label_rh = pe.Node(interface=freesurfer.MRIsCALabel(), name="ca_label_rh")
    ca_label_rh.inputs.hemisphere = "rh"

    aparc2aseg = pe.Node(interface=freesurfer.Aparc2Aseg(), name="aparc2aseg")
    aparc2aseg.inputs.label_wm = False
    aparc2aseg.inputs.rip_unknown = True
    aparc2aseg.inputs.copy_inputs = True

    ## Rename outputs
    generate_annot_filename_lh = Node(Function(
            input_names=["atlas", "hemi", "subject"],
            output_names=["subject_annot"],
            function=_generate_annot_filename),
            name=f"generate_annot_filename_lh"
        )
    generate_annot_filename_lh.inputs.hemi = "lh"
    rename_annot_bids_lh = Node(Rename(), name=f"rename_annot_bids_lh")

    generate_annot_filename_rh = Node(Function(
            input_names=["atlas", "hemi", "subject"],
            output_names=["subject_annot"],
            function=_generate_annot_filename),
            name=f"generate_annot_filename_rh"
        )
    generate_annot_filename_rh.inputs.hemi = "rh"
    rename_annot_bids_rh = Node(Rename(), name=f"rename_annot_bids_rh")


    # Workflow
    ## Inputs
    workflow.connect(inputnode, "subject_id", fs_both, "subject_id")
    workflow.connect(inputnode, "subjects_dir", fs_both, "subjects_dir")

    workflow.connect(inputnode, "subject_id", fs_rh, "subject_id")
    workflow.connect(inputnode, "subjects_dir", fs_rh, "subjects_dir")

    workflow.connect(inputnode, "subject_id", fs_lh, "subject_id")
    workflow.connect(inputnode, "subjects_dir", fs_lh, "subjects_dir")

    workflow.connect(inputnode, "subject_id", ca_label_lh, "subject_id")
    workflow.connect(inputnode, "subjects_dir", ca_label_lh, "subjects_dir")

    workflow.connect(inputnode, "subject_id", ca_label_rh, "subject_id")
    workflow.connect(inputnode, "subjects_dir", ca_label_rh, "subjects_dir")

    workflow.connect(inputnode, "subject_id", aparc2aseg, "subject_id")
    workflow.connect(inputnode, "subjects_dir", aparc2aseg, "subjects_dir")

    workflow.connect(inputnode, "atlas_name", gen_inputs, "atlas_name")
    workflow.connect(inputnode, "subject_id", gen_inputs, "subject_id")
    workflow.connect(inputnode, "subjects_dir", gen_inputs, "subjects_dir")
    workflow.connect(
        inputnode, "data_dir", gen_inputs, "data_dir"
    )

    ## Connect Existing files
    workflow.connect(fs_both, "ribbon", select_ribbon, "inlist")
    ## ca_label_rh
    workflow.connect(fs_rh, "sphere_reg", ca_label_rh, "canonsurf")
    workflow.connect(fs_rh, "smoothwm", ca_label_rh, "smoothwm")
    workflow.connect(fs_rh, "sulc", ca_label_rh, "sulc")
    workflow.connect(fs_rh, "curv", ca_label_rh, "curv")
    workflow.connect(gen_inputs, "rh_gcs_path", ca_label_rh, "classifier")
    workflow.connect(gen_inputs, "rh_fname", ca_label_rh, "out_file")
    ## ca_label_lh
    workflow.connect(fs_lh, "sphere_reg", ca_label_lh, "canonsurf")
    workflow.connect(fs_lh, "smoothwm", ca_label_lh, "smoothwm")
    workflow.connect(fs_lh, "sulc", ca_label_lh, "sulc")
    workflow.connect(fs_lh, "curv", ca_label_lh, "curv")
    workflow.connect(gen_inputs, "lh_gcs_path", ca_label_lh, "classifier")
    workflow.connect(gen_inputs, "lh_fname", ca_label_lh, "out_file")
    ## aparc2aseg
    workflow.connect(gen_inputs, "annot_command", aparc2aseg, "args")
    workflow.connect(fs_both, "aseg", aparc2aseg, "aseg")
    workflow.connect(select_ribbon, "out", aparc2aseg, "ribbon")
    workflow.connect(fs_rh, "white", aparc2aseg, "rh_white")
    workflow.connect(fs_rh, "pial", aparc2aseg, "rh_pial")
    workflow.connect(fs_rh, "ribbon", aparc2aseg, "rh_ribbon")
    workflow.connect(fs_lh, "white", aparc2aseg, "lh_white")
    workflow.connect(fs_lh, "pial", aparc2aseg, "lh_pial")
    workflow.connect(fs_lh, "ribbon", aparc2aseg, "lh_ribbon")
    workflow.connect(ca_label_lh, "out_file", aparc2aseg, "lh_annotation")
    workflow.connect(ca_label_rh, "out_file", aparc2aseg, "rh_annotation")
    workflow.connect(gen_inputs, "label_fname", aparc2aseg, "out_file")

    ## rename
    workflow.connect(inputnode, "atlas_name", generate_annot_filename_lh, "atlas")
    workflow.connect(inputnode, "subject_id", generate_annot_filename_lh, "subject")
    workflow.connect(inputnode, "atlas_name", generate_annot_filename_rh, "atlas")
    workflow.connect(inputnode, "subject_id", generate_annot_filename_rh, "subject")

    workflow.connect(generate_annot_filename_lh, "subject_annot", rename_annot_bids_lh, "format_string")
    workflow.connect(ca_label_lh, "out_file", rename_annot_bids_lh, "in_file")
    workflow.connect(generate_annot_filename_rh, "subject_annot", rename_annot_bids_rh, "format_string")
    workflow.connect(ca_label_rh, "out_file", rename_annot_bids_rh, "in_file")

    ## Outputs
    outputnode = Node(
        interface=IdentityInterface(
            fields=[
                "volume",
                "lh_aseg",
                "rh_aseg",
                "atlas_name",
                "lut",
                "subject_id",
                "subjects_dir",
            ]
        ),
        name="outputnode",
    )
    workflow.connect(aparc2aseg, "out_file", outputnode, "volume")
    workflow.connect(rename_annot_bids_lh, "out_file", outputnode, "lh_aseg")
    workflow.connect(rename_annot_bids_rh, "out_file", outputnode, "rh_aseg")

    workflow.connect(inputnode, "subject_id", outputnode, "subject_id")
    workflow.connect(inputnode, "subjects_dir", outputnode, "subjects_dir")
    workflow.connect(gen_inputs, "atlas_name", outputnode, "atlas_name")
    workflow.connect(gen_inputs, "lut_path", outputnode, "lut")
    return workflow
