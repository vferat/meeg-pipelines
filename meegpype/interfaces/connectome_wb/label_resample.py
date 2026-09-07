import os
from nipype.interfaces.base import (
    TraitedSpec,
    CommandLineInputSpec,
    CommandLine,
    File,
    traits,
)


class LabelResampleInputSpec(CommandLineInputSpec):
    label_in = File(
        desc="the label file to resample",
        exists=True,
        mandatory=True,
        argstr="%s",
        position=0,
    )
    current_sphere = File(
        desc="a sphere surface with the mesh that the label file is currently on",
        exists=True,
        mandatory=True,
        argstr="%s",
        position=1,
    )
    new_sphere = File(
        desc="a sphere surface that is in register with <current-sphere> and has the desired output mesh",
        exists=True,
        mandatory=True,
        argstr="%s",
        position=2,
    )
    method = traits.Str(
        desc="the method name", exists=True, mandatory=True, argstr="%s", position=3
    )
    label_out = File(
        desc="the output label file",
        exists=False,
        mandatory=True,
        argstr="%s",
        position=4,
    )
    area_metrics = traits.List(
        File(exists=True),
        minlen=2,
        maxlen=2,
        sep=" ",
        desc="area metric files",
        mandatory=False,
        argstr="-area-metrics %s",
    )


class LabelResampleOutputSpec(TraitedSpec):
    out = File(desc="the output file", exists=True)


class LabelResample(CommandLine):
    input_spec = LabelResampleInputSpec
    output_spec = LabelResampleOutputSpec
    _cmd = "wb_command -label-resample"

    def _list_outputs(self):
        cwd = os.getcwd()
        out_path = os.path.join(cwd, self.inputs.label_out)
        outputs = self.output_spec().get()
        outputs["out"] = out_path
        return outputs
