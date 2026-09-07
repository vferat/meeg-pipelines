import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    TraitedSpec,
    isdefined,
)
import mne


class DecimateSurfaceInputSpec(BaseInterfaceInputSpec):
    input_surface = traits.File(
        desc="The path to a Freesurfer surface mesh in triangular format.",
        mandatory=True,
    )
    output_surface = traits.File(
        desc="The path to the decimated output surface mesh.",
        mandatory=True,
    )
    n_triangles = traits.Int(desc="he desired number of triangles.", mandatory=True)
    method = traits.Str(desc="Can be “quadric” or “sphere”. “sphere” will inflate the surface to a sphere using Freesurfer and downsample to an icosahedral or octahedral mesh.", mandatory=True)


class DecimateSurfaceOutputSpec(TraitedSpec):
    output_surface = traits.File(
        desc="The path to the decimated output surface mesh.",
        exists=True,
    )


class DecimateSurface(BaseInterface):
    input_spec = DecimateSurfaceInputSpec
    output_spec = DecimateSurfaceOutputSpec

    def _run_interface(self, runtime):
        args = dict()
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                args[key] = value

        mesh = mne.read_surface(args["input_surface"], read_metadata=True)
        decimated_mesh = mne.decimate_surface(
            mesh[0], mesh[1], n_triangles=args["n_triangles"], method=args["method"]
        )
        mne.write_surface(
            args["output_surface"],
            decimated_mesh[0],
            decimated_mesh[1],
            volume_info=mesh[2],
            overwrite=True,
        )
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["output_surface"] = os.path.abspath(self.inputs.output_surface)
        return outputs
