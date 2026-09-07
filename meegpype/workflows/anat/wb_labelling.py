import os
from nipype import Node, Workflow

from nipype.interfaces.utility import IdentityInterface, Function, Rename, Merge
from nipype.interfaces.freesurfer import SurfaceTransform, MRIsConvert
from nipype.interfaces.io import FreeSurferSource, ExportFile

from ...interfaces.freesurfer import Aparc2Aseg
from ...interfaces.connectome_wb import LabelResample
from ...data import get_data_folder


def _generate_hemi_filenames(
    atlas, hemi, subject, subjects_dir, template, templates_dir, data_dir
):
    import os
    hemi_alias = "R" if hemi == "rh" else "L"

    # fs_LR
    fsLR_dir = os.path.join(data_dir, "fsLR")
    fsLR_label = f"atlas_{atlas}.{hemi_alias}.32k_fs_LR.label.gii"
    fsLR_label = os.path.join(fsLR_dir, fsLR_label)

    fsLR_deformed_to_template_sphere = (
        f"fs_LR-deformed_to-{template}.{hemi_alias}.sphere.32k_fs_LR.surf.gii"
    )
    fsLR_deformed_to_template_sphere = os.path.join(
        fsLR_dir, fsLR_deformed_to_template_sphere
    )

    area_in = f"fs_LR.{hemi_alias}.midthickness_va_avg.32k_fs_LR.shape.gii"
    area_in = os.path.join(fsLR_dir, area_in)

    # template
    template_dir = os.path.join(templates_dir, template)
    area_out = (
        f"{template}.{hemi_alias}.midthickness_va_avg.164k_fsavg_{hemi_alias}.shape.gii"
    )
    area_out = os.path.join(template_dir, area_out)

    template_label = (
        f"{template}_hemi-{hemi_alias}_space-{template}_desc-{atlas}.label.gii"
    )
    template_annot = (
        f"{template}_hemi-{hemi_alias}_space-{template}_desc-{atlas}.annot"
    )

    # subject
    subject_annot = f"{hemi}.{atlas}.annot"
    subject_annot = os.path.abspath(os.path.join(subjects_dir, subject, "label", subject_annot))
    area_metrics = [area_in, area_out]

    LUT = os.path.join(data_dir, "fsLR", f"{atlas}_LUT.txt")
    return (
        fsLR_label,
        fsLR_deformed_to_template_sphere,
        area_metrics,
        template_label,
        template_annot,
        subject_annot,
        LUT,
    )


def _generate_dseg_filename(atlas, subject):
    from meegpype.data.fsLR import ATLAS
    atlas_dict = next((item for item in ATLAS if item["name"] == atlas), None)
    if atlas_dict is None:
        raise ValueError(f"Atlas {atlas} not found in ATLAS.")
    else:
        label_fname = f"{subject}_space-fsnative_atlas-{atlas_dict['atlas']}"
        if "seg" in atlas_dict:
            label_fname += f"_seg-{atlas_dict['seg']}"
        if "scale" in atlas_dict:
            label_fname += f"_scale-{atlas_dict['scale']}"
        label_fname += "_dseg.nii"
    return label_fname


def _generate_annot_filename(atlas, hemi, subject):
    from meegpype.data.fsLR import ATLAS
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


def generate_wb_labelling_workflow(name="wb_labelling", base_dir=None):
    # Initiation of a workflow
    wf = Workflow(name=name, base_dir=base_dir)

    # Inputs
    inputnode = Node(
        IdentityInterface(
            fields=["atlas", "subject", "subjects_dir"], mandatory_inputs=True
        ),
        name="inputnode",
    )

    # Merge
    merge = Node(Merge(2), name="merge_annot")

    # Aparc2aseg
    gen_dseg_filename = Node(
        name="generate_dseg_filename",
        interface=Function(
            input_names=["atlas", "subject"],
            output_names=["dseg_filename"],
            function=_generate_dseg_filename,
        ),
    )

    aparc2aseg = Node(Aparc2Aseg(), name="aparc2aseg")
    aparc2aseg.inputs.new_ribbon = True

    template = "fsaverage"
    templates_dir = os.path.join(get_data_folder(), "freesurfer")

    # outputs
    outputnode = Node(IdentityInterface(fields=["aseg", "annot_rh", "annot_lh", "LUT"]), name="outputnode")

    # TODO: add fsaverage data (pial, sphere) to data folder and use files shipped with library
    # Hemispheres
    for h, hemi in enumerate(["lh", "rh"]):
        # Generate filenames
        gen_filenames = Node(
            name=f"generate_filenames_{hemi}",
            interface=Function(
                input_names=[
                    "atlas",
                    "hemi",
                    "subject",
                    "subjects_dir",
                    "template",
                    "templates_dir",
                    "data_dir",
                ],
                output_names=[
                    "fsLR_label",
                    "fsLR_deformed_to_template_sphere",
                    "area_metrics",
                    "template_label",
                    "template_annot",
                    "subject_annot",
                    "LUT",
                ],
                function=_generate_hemi_filenames,
            ),
        )
        gen_filenames.inputs.hemi = hemi
        gen_filenames.inputs.template = template
        gen_filenames.inputs.templates_dir = templates_dir
        gen_filenames.inputs.data_dir = get_data_folder()

        # template input
        template_source = Node(FreeSurferSource(), name=f"template_{hemi}")
        template_source.inputs.hemi = hemi
        template_source.inputs.subject_id = template
        template_source.inputs.subjects_dir = templates_dir

        # fsaverage label.gii to .annot
        convert_template_sphere = Node(
            MRIsConvert(), name=f"convert_template_sphere_{hemi}"
        )
        convert_template_sphere.inputs.out_datatype = "gii"

        # fsLR to template
        resample2template = Node(LabelResample(), name=f"resample2template_{hemi}")
        resample2template.inputs.method = "ADAP_BARY_AREA"

        # fsaverage label.gii to .annot
        convert2annot = Node(MRIsConvert(), name=f"convert2annot_{hemi}")

        # fsaverage to subject
        surf2surf = Node(SurfaceTransform(), name=f"surf2surf_{hemi}")
        surf2surf.inputs.source_subject = template
        surf2surf.inputs.hemi = hemi

        # rename for aparc2aseg
        export_annot_apar2aseg = Node(ExportFile(), name=f"export_annot_apar2aseg_{hemi}")
        export_annot_apar2aseg.inputs.clobber = True

        # rename for output
        generate_annot_filename = Node(Function(
            input_names=["atlas", "hemi", "subject"],
            output_names=["subject_annot"],
            function=_generate_annot_filename),
            name=f"generate_annot_filename_{hemi}"
        )
        generate_annot_filename.inputs.hemi = hemi
        rename_annot_bids = Node(Rename(), name=f"rename_annot_bids_{hemi}")

        # Connect the nodes
        wf.connect(inputnode, "atlas", gen_filenames, "atlas")
        wf.connect(inputnode, "subject", gen_filenames, "subject")
        wf.connect(inputnode, "subjects_dir", gen_filenames, "subjects_dir")

        wf.connect(inputnode, "subject", surf2surf, "target_subject")
        wf.connect(inputnode, "subjects_dir", surf2surf, "subjects_dir")

        wf.connect(template_source, "sphere", convert_template_sphere, "in_file")

        wf.connect(gen_filenames, "fsLR_label", resample2template, "label_in")
        wf.connect(
            gen_filenames,
            "fsLR_deformed_to_template_sphere",
            resample2template,
            "current_sphere",
        )
        wf.connect(gen_filenames, "template_label", resample2template, "label_out")
        wf.connect(gen_filenames, "area_metrics", resample2template, "area_metrics")
        wf.connect(
            convert_template_sphere, "converted", resample2template, "new_sphere"
        )

        wf.connect(template_source, "pial", convert2annot, "in_file")
        wf.connect(resample2template, "out", convert2annot, "annot_file")
        wf.connect(gen_filenames, "template_annot", convert2annot, "out_file")

        wf.connect(convert2annot, "converted", surf2surf, "source_annot_file")

        wf.connect(surf2surf, "out_file", export_annot_apar2aseg, "in_file")
        wf.connect(gen_filenames, "subject_annot", export_annot_apar2aseg, "out_file")
        wf.connect(export_annot_apar2aseg, "out_file", merge, f"in{h+1}")

        # BIDS like
        wf.connect(inputnode, "atlas", generate_annot_filename, "atlas")
        wf.connect(inputnode, "subject", generate_annot_filename, "subject")
        wf.connect(surf2surf, "out_file", rename_annot_bids, "in_file")
        wf.connect(generate_annot_filename, "subject_annot", rename_annot_bids, "format_string")
        wf.connect(rename_annot_bids, "out_file", outputnode, f"annot_{hemi}")



    wf.connect(inputnode, "atlas", gen_dseg_filename, "atlas")
    wf.connect(inputnode, "subject", gen_dseg_filename, "subject")

    wf.connect(inputnode, "subject", aparc2aseg, "subject")
    wf.connect(inputnode, "subjects_dir", aparc2aseg, "subjects_dir")
    wf.connect(inputnode, "atlas", aparc2aseg, "atlas")
    wf.connect(gen_dseg_filename, "dseg_filename", aparc2aseg, "out_file")
    wf.connect(merge, "out", aparc2aseg, "annot_files")


    wf.connect(aparc2aseg, "out", outputnode, "aseg")
    wf.connect(gen_filenames, "LUT", outputnode, "LUT")
    return wf
