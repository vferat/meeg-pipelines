import os
from nipype.interfaces.base import (
    TraitedSpec,
    File,
    traits)
from nipype.interfaces.freesurfer.base import FSTraitedSpec, FSCommand


class MRIsSmoothInputSpec(FSTraitedSpec):
    # required
    input_surface = File(
        position=2,
        argstr="%s",
        exists=True,
        mandatory=True,
        desc="input_surface",
    )
    output_surface = File(
        position=3,
        argstr="%s",
        exists=False,
        mandatory=True,
        desc="output_surface",
    )
    average  = traits.Int(
        position=0,
        mandatory=False,
        argstr="-a %d",
        desc="specify # of curvature averaging iterations (def=10).",
    )
    n_iteration  = traits.Int(
        position=1,
        mandatory=False,
        argstr="-n %d",
        desc="specify # of smoothing iterations (def=10).",
    )


class MRIsSmoothOutputSpec(TraitedSpec):
    output_surface = File(desc="the output file", exists=True)


class MRIsSmooth(FSCommand):
    input_spec = MRIsSmoothInputSpec
    output_spec = MRIsSmoothOutputSpec
    _cmd = 'mris_smooth'

    def _list_outputs(self):
        cwd = os.getcwd()
        out_path = os.path.join(cwd, self.inputs.output_surface)
        outputs = self.output_spec().get()
        outputs['output_surface'] = out_path
        return outputs
