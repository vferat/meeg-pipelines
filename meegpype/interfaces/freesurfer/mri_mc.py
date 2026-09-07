import os
from nipype.interfaces.base import (
    TraitedSpec,
    File,
    traits)
from nipype.interfaces.freesurfer.base import FSTraitedSpec, FSCommand


class MRImcInputSpec(FSTraitedSpec):
    # required
    input_volume = File(
        position=0,
        argstr="%s",
        exists=True,
        mandatory=True,
        desc="input_volume",
    )
    label_value  = traits.Int(
        position=1,
        argstr="%d",
        mandatory=True,
        desc="label_value",
    )
    output_surface = File(
        position=2,
        argstr="%s",
        exists=False,
        mandatory=True,
        desc="Full path of file to save the output segmentation in",
    )


class MRImcOutputSpec(TraitedSpec):
    output_surface = File(desc="the output file", exists=True)


class MRImc(FSCommand):
    input_spec = MRImcInputSpec
    output_spec = MRImcOutputSpec
    _cmd = 'mri_mc'

    def _list_outputs(self):
        cwd = os.getcwd()
        out_path = os.path.join(cwd, self.inputs.output_surface)
        outputs = self.output_spec().get()
        outputs['output_surface'] = out_path
        return outputs
