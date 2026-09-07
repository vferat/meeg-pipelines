import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    TraitedSpec,
    isdefined,
    Directory,
    File,
)
import mne.bem


class MakeWatershedBEMInputSpec(BaseInterfaceInputSpec):
    subject = traits.Str(desc="Subject name (required)", mandatory=True)
    subjects_dir = Directory(desc="Subjects directory", exists=True, mandatory=True)
    volume = traits.Str(desc="Defaults to T1.", mandatory=False, default="T1")
    atlas = traits.Bool(
        desc="Specify the --atlas option for mri_watershed.",
        mandatory=False,
        default=False,
    )
    gcaatlas = traits.Bool(
        desc="Specify the --brain_atlas option for mri_watershed.",
        mandatory=False,
        default=False,
    )
    preflood = traits.Float(
        desc="Change the preflood height.", mandatory=False, default=None
    )
    copy = traits.Bool(
        desc="If True (default), use copies instead of symlinks for surfaces (if they do not already exist).",
        mandatory=False,
        default=True,
    )
    T1 = traits.Bool(
        desc="If True, pass the -T1 flag. By default (None), this takes the same value as gcaatlas.",
        mandatory=False,
        default=None,
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    brainmask = traits.File(
        desc="The filename for the brainmask output file, Can be for example '../../mri/brainmask.mgz' to overwrite the brainmask obtained via recon-all -autorecon1.",
        mandatory=False,
        default="ws.mgz",
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class MakeWatershedBEMOutputSpec(TraitedSpec):
    subject = traits.Str(desc="Subject name")
    subjects_dir = Directory(desc="Subjects directory")
    brain_surf = traits.File(des="Brain surface", exists=True)
    inner_skull = traits.File(des="Inner skull surface", exists=True, hash_files=False)
    outer_skin = traits.File(des="Outer skin surface", exists=True, hash_files=False)
    outer_skull = traits.File(des="Outer skull surface", exists=True, hash_files=False)
    head = traits.File(des="Head model", exists=True, hash_files=False)


class MakeWatershedBEM(BaseInterface):
    input_spec = MakeWatershedBEMInputSpec
    output_spec = MakeWatershedBEMOutputSpec

    def _run_interface(self, runtime):
        args = dict()
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                args[key] = value

        subject_dir = args["subjects_dir"] + "/" + args["subject"]
        if "brainmask" in args.keys():
            relative_path = os.path.relpath(args["brainmask"], subject_dir)
            args["brainmask"] = relative_path

        mne.bem.make_watershed_bem(**args)
        return runtime

    def _list_outputs(self):
        subject = self.inputs.subject
        subjects_dir = self.inputs.subjects_dir
        subject_dir = subjects_dir + "/" + subject

        outputs = self.output_spec().get()
        outputs["subject"] = subject
        outputs["subjects_dir"] = subjects_dir

        outputs["brain_surf"] = os.path.join(subject_dir, "bem", "brain.surf")
        outputs["inner_skull"] = os.path.join(subject_dir, "bem", "inner_skull.surf")
        outputs["outer_skin"] = os.path.join(subject_dir, "bem", "outer_skin.surf")
        outputs["outer_skull"] = os.path.join(subject_dir, "bem", "outer_skull.surf")
        outputs["head"] = os.path.join(subject_dir, "bem", f"{subject}-head.fif")
        return outputs


class SetupForwardModelInputSpec(TraitedSpec):
    fname = traits.File(
        desc="Output base name. Will be prepend by -bem.fif and -sol.fif",
        exists=False,
        mandatory=True,
    )
    subject = traits.Str(desc="Subject name (required)", mandatory=True)
    subjects_dir = Directory(desc="Subjects directory", exists=True, mandatory=True)
    ico = traits.Int(
        desc="The surface ico downsampling to use, e.g. 5=20484, 4=5120, 3=1280. If None, no subsampling is applied.",
        mandatory=False,
    )
    conductivity = traits.Array(
        desc="Defines the brain compartment conductivity. The default value is 0.3 S/m.",
        mandatory=False,
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=False,
    )


class SetupForwardModelOutputSpec(TraitedSpec):
    bem_surfaces = File(
        desc="The resulting file containing the BEM model.", exists=True
    )
    bem_solution = File(
        desc="The resulting file containing the BEM solution.", exists=True
    )


class SetupForwardModel(BaseInterface):
    input_spec = SetupForwardModelInputSpec
    output_spec = SetupForwardModelOutputSpec

    def _run_interface(self, runtime):
        inputs = {
            "ico": 4,
            "conductivity": (0.3, 0.006, 0.3),
            "overwrite": False,
            "verbose": None,
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fname = inputs["fname"]
        subject = inputs["subject"]
        subjects_dir = inputs["subjects_dir"]
        ico = inputs["ico"]
        conductivity = inputs["conductivity"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        cwd = os.getcwd()
        bem_surfaces = mne.make_bem_model(
            subject,
            ico=ico,
            conductivity=conductivity,
            subjects_dir=subjects_dir,
            verbose=verbose,
        )
        fname_surfaces = os.path.join(cwd, fname + "-bem.fif")
        mne.write_bem_surfaces(
            fname_surfaces, bem_surfaces, overwrite=overwrite, verbose=verbose
        )

        bem_solution = mne.make_bem_solution(
            bem_surfaces, solver="mne", verbose=verbose
        )
        fname_solution = os.path.join(cwd, fname + "-sol.fif")
        mne.write_bem_solution(
            fname_solution, bem_solution, overwrite=overwrite, verbose=verbose
        )
        return runtime

    def _list_outputs(self):
        fname = self.inputs.fname
        outputs = self.output_spec().get()
        cwd = os.getcwd()
        fname_surfaces = os.path.join(cwd, fname + "-bem.fif")
        outputs["bem_surfaces"] = fname_surfaces

        fname_solution = os.path.join(cwd, fname + "-sol.fif")
        outputs["bem_solution"] = fname_solution
        return outputs
