import os

from nipype.interfaces.base import (
    TraitedSpec,
    File,
    traits)
from nipype.interfaces.freesurfer.base import FSTraitedSpec, FSCommand


class MRIBinarizeInputSpec(FSTraitedSpec):
    # required
    input_volume = File(
        argstr="--i %s",
        exists=True,
        mandatory=True,
        desc="input volume",
    )
    output_volume = File(
        argstr="--o %s",
        exists=False,
        mandatory=True,
        desc="output volume",
    )
    match = traits.Int(
        mandatory=False,
        argstr="--match %d",
        desc="match",
    )
    inv = traits.Bool(
        mandatory=False,
        argstr="--inv",
        desc="inverse.",
    )

class MRIBinarizeOutputSpec(TraitedSpec):
    output_volume = File(desc="the output volume.", exists=True)   
        

class MRIBinarize(FSCommand):
    input_spec = MRIBinarizeInputSpec
    output_spec = MRIBinarizeOutputSpec
    _cmd = 'mri_binarize'

    def _list_outputs(self):
        cwd = os.getcwd()
        out_path = os.path.join(cwd, self.inputs.output_volume)
        outputs = self.output_spec().get()
        outputs['output_volume'] = out_path
        return outputs