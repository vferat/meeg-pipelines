import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    TraitedSpec,
    isdefined,
    Directory,
)
import mne


class MakeHeadSurfaceInputSpec(BaseInterfaceInputSpec):
    subject = traits.Str(desc="Subject ID (required)", mandatory=True)
    subjects_dir = Directory(desc="Subjects directory", exists=True, mandatory=True)
    force = traits.Bool(desc="Force creation of the surface even if it has some topological defects.", mandatory=False)
    no_decimate = traits.Bool(desc='Disable the “medium” and “sparse” decimations. In this case, only a “dense” surface will be generated.', mandatory=False)
    threshold = traits.Int(desc='The threshold to use with the MRI in the call to mkheadsurf. The default is 20.', mandatory=False, min=0)
    mri = traits.Str(
        desc="The MRI to use. Should exist in '$SUBJECTS_DIR/$SUBJECT/mri'.",
        mandatory=False,
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class MakeHeadSurfaceOutputSpec(TraitedSpec):
    head_dense = traits.File(desc="High density head surface file.", exists=True)
    subject = traits.Str(desc="Subject ID")
    subjects_dir = Directory(desc="Subjects directory")


class MakeHeadSurface(BaseInterface):
    input_spec = MakeHeadSurfaceInputSpec
    output_spec = MakeHeadSurfaceOutputSpec

    def _run_interface(self, runtime):
        inputs = {
            "force": True,
            "no_decimate": False,
            "threshold": 20,
            "mri": "T1.mgz",
            "overwrite": False,
            "verbose": None,
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        subject = inputs["subject"]
        subjects_dir = inputs["subjects_dir"]
        force = inputs["force"]
        no_decimate = inputs["no_decimate"]
        threshold = inputs["threshold"]
        mri = inputs["mri"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        mne.bem.make_scalp_surfaces(subject,
                                    subjects_dir=subjects_dir,
                                    force=force,
                                    overwrite=overwrite,
                                    no_decimate=no_decimate,
                                    threshold=threshold,
                                    mri=mri,
                                    verbose=verbose)

        # Outputs
        self.head_dense = os.path.join(subjects_dir, subject, "bem", f"{subject}-head-dense.fif")
        self.subject = subject
        self.subjects_dir = subjects_dir
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["head_dense"] = self.head_dense
        outputs["subject"] = self.subject
        outputs["subjects_dir"] = self.subjects_dir
        return outputs
