import os
from nipype.interfaces.base import (
    TraitedSpec,
    File,
    Directory,
    traits)
from nipype.interfaces.freesurfer.base import FSTraitedSpec, FSCommand


class Aparc2AsegInputSpec(FSTraitedSpec):
    # required
    subject = traits.String(
        "subject_id",
        argstr="--s %s",
        usedefault=True,
        mandatory=True,
        desc="Subject being processed",
    )
    subjects_dir = Directory(desc="Subjects directory",
                                exists=True,
                                mandatory=True)
    out_file = File(
        argstr="--o %s",
        exists=False,
        mandatory=True,
        desc="Full path of file to save the output segmentation in",
    )
    # optional
    old_ribbon = traits.Bool(
        argstr="--old-ribbon",
        mandatory=False,
        desc="use mri/hemi.ribbon.mgz as a mask for the cortex",
        xor=["new_ribbon"],
    )
    new_ribbon = traits.Bool(
        argstr="--new-ribbon",
        mandatory=False,
        desc="use mri/hemi.ribbon.mgz as a mask for the cortex",
        xor=["old_ribbon"],
    )
    atlas = traits.String(
        argstr="--annot %s",
        mandatory=False,
        desc="use specified label file instead of aparc"
    )
    annot_files = traits.List(
        File(exists=True),
        desc="Make sure annot files are computed")


class Aparc2AsegOutputSpec(TraitedSpec):
    out = File(desc="the output file", exists = True)


class Aparc2Aseg(FSCommand):
    input_spec = Aparc2AsegInputSpec
    output_spec = Aparc2AsegOutputSpec
    _cmd = 'mri_aparc2aseg'

    def _list_outputs(self):
        cwd = os.getcwd()
        out_path = os.path.join(cwd, self.inputs.out_file)
        outputs = self.output_spec().get()
        outputs['out'] = out_path
        return outputs
