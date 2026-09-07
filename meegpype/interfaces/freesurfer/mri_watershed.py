import os
from nipype.interfaces.base import (
    TraitedSpec,
    File,
    traits)
from nipype.interfaces.freesurfer.base import FSTraitedSpec, FSCommand


class MRIWatershedInputSpec(FSTraitedSpec):
    # required
    invol = File(
        argstr="%s",
        position=-2,
        exists=True,
        mandatory=True,
        desc="input volume",
    )
    outvol = File(
        argstr="%s",
        position=-1,
        exists=False,
        mandatory=True,
        desc="output volume",
    )
    # optional
    surf = traits.String(
        argstr="-surf %s",
        mandatory=False,
        desc="save the BEM surfaces."
    )
    useSRAS = traits.Bool(
        argstr="-useSRAS",
        mandatory=False,
        desc="use the SRAS coordinate system.",
    )
    n = traits.Bool(
        argstr="-n",
        mandatory=False,
        desc="not use the watershed analyze process.",
    )
    h = traits.Float(
        argstr="-h %f",
        mandatory=False,
        desc="precize the preflooding height (in percent).",
    )
    T1 = traits.Bool(
        argstr="-T1",
        mandatory=False,
        desc="specify T1 input volume (T1 grey value = 110).",
    )


class MRIWatershedOutputSpec(TraitedSpec):
    brainvol = File(desc="skull stripped brain volume", exists=True, mandatory=True)
    surf_brain_surface = File(desc="brain surface", exists=True)
    surf_inner_skull_surface = File(desc="inner skull surface", exists=True)
    surf_outer_skin_surface = File(desc="outer skin surface", exists=True)
    surf_outer_skull_surface = File(desc="outer skull surface", exists=True)


class MRIWatershed(FSCommand):
    input_spec = MRIWatershedInputSpec
    output_spec = MRIWatershedOutputSpec
    _cmd = 'mri_watershed'

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['brainvol'] =  self.inputs.outvol

        if self.inputs.surf:
            cwd = os.getcwd()
            outputs['surf_brain_surface'] = os.path.join(cwd, self.inputs.surf + "_brain_surface")
            outputs['surf_inner_skull_surface'] = os.path.join(cwd, self.inputs.surf + "_inner_skull_surface")
            outputs['surf_outer_skin_surface'] = os.path.join(cwd, self.inputs.surf + "_outer_skin_surface")
            outputs['surf_outer_skull_surface'] = os.path.join(cwd, self.inputs.surf +"_outer_skull_surface")
        return outputs
