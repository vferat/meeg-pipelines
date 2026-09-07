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
import mne


class SetupSurfaceSourceSpaceInputSpec(BaseInterfaceInputSpec):
    fname = traits.File(
        desc="Output file name. Use a name <dir>/<name>-src.fif.", mandatory=True
    )
    subject = traits.Str(
        desc="Subject name (required)", mandatory=True, argstr="--subject %s"
    )
    subjects_dir = Directory(
        desc="Subjects directory",
        exists=True,
        mandatory=True,
        argstr="--subjects-dir=%s",
    )
    spacing = traits.Either(
        traits.Str,
        traits.Int,
        desc="The spacing to use. Can be 'ico#' for a recursively subdivided icosahedron,"
        "'oct#' for a recursively subdivided octahedron, 'all' for all points, or an"
        " integer to use approximate distance-based spacing (in mm)..",
        mandatory=False,
        default="oct6",
    )
    surface = traits.Str(desc="The surface to use", mandatory=False, default="white")
    add_dist = traits.Enum(
        True,
        False,
        "patch",
        desc="Add distances. Can be 'True', 'False', or 'patch' to only compute cortical patch statistics (like the –cps option in MNE-C).",
        mandatory=False,
    )
    n_jobs = traits.Enum(
        1,
        2,
        desc="The number of jobs to run in parallel (default 1). Requires the joblib package. Will use at most 2 jobs (one for each hemisphere).",
        mandatory=False,
        default=1,
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=False,
    )


class SetupSurfaceSourceSpaceOutputSpec(TraitedSpec):
    src = File(desc="The resulting source space.", exists=True)


class SetupSurfaceSourceSpace(BaseInterface):
    input_spec = SetupSurfaceSourceSpaceInputSpec
    output_spec = SetupSurfaceSourceSpaceOutputSpec

    def _run_interface(self, runtime):
        inputs = {
            "spacing": "oct6",
            "surface": "white",
            "add_dist": True,
            "n_jobs": 1,
            "overwrite": False,
            "verbose": None,
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fname = inputs["fname"]
        subject = inputs["subject"]
        subjects_dir = inputs["subjects_dir"]
        spacing = inputs["spacing"]
        surface = inputs["surface"]
        add_dist = inputs["add_dist"]
        n_jobs = inputs["n_jobs"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        cwd = os.getcwd()
        src = mne.setup_source_space(
            subject,
            spacing=spacing,
            surface=surface,
            subjects_dir=subjects_dir,
            add_dist=add_dist,
            n_jobs=n_jobs,
            verbose=verbose,
        )
        fname_src = os.path.join(cwd, fname + "-src.fif")
        mne.write_source_spaces(fname_src, src, overwrite=overwrite, verbose=verbose)

        return runtime

    def _list_outputs(self):
        fname = self.inputs.fname
        outputs = self.output_spec().get()
        cwd = os.getcwd()
        fname_src = os.path.join(cwd, fname + "-src.fif")
        outputs["src"] = fname_src
        return outputs


class SetupVolumeSourceSpaceInputSpec(BaseInterfaceInputSpec):
    fname = traits.File(
        desc="Output file name. Use a name <dir>/<name>-src.fif.", mandatory=True
    )
    subject = traits.Str(desc="Subject name (required)", mandatory=True)
    subjects_dir = traits.Directory(
        desc="Subjects directory", exists=True, mandatory=False, default=None
    )
    pos = traits.Float(
        desc="Positions to use for sources. A grid will be constructed with the spacing given by pos in mm, generating a volume source space.",
        units="mm",
        mandatory=False,
        default=5.0,
    )
    mri = traits.Either(
        None,
        traits.File(exists=True),
        desc="The filename of an MRI volume (mgh or mgz) to create the interpolation matrix over. Source estimates obtained in the volume source space can then be morphed onto the MRI volume using this interpolator.",
        mandatory=False,
        default=None,
    )
    sphere = traits.ArrayOrNone(
        shape=(4,),
        desc="Define spherical source space bounds using origin and radius given by (Ox, Oy, Oz, rad) in sphere_units.",
        mandatory=False,
        default=None,
        xor=["bem", "surface"],
    )
    bem = traits.File(
        desc="Define source space bounds using a BEM file (specifically the inner skull surface).",
        exists=True,
        mandatory=False,
        default=None,
        xor=["sphere", "surface"],
    )
    surface = traits.File(
        desc="Define source space bounds using a FreeSurfer surface file.",
        exists=True,
        mandatory=False,
        default=None,
        xor=["bem"],
    )
    mindist = traits.Float(
        desc="Exclude points closer than this distance (mm) to the bounding surface.",
        units="mm",
        mandatory=False,
        default=5.0,
    )
    exclude = traits.Float(
        desc="Exclude points closer than this distance (mm) from the center of mass of the bounding surface.",
        units="mm",
        mandatory=False,
        default=0.0,
    )
    volume_label = traits.List(
        desc="Region(s) of interest to use. None (default) will create a single whole-brain source space. Otherwise, a separate source space will be created for each entry in the list or dict (str will be turned into a single-element list). Standard Freesurfer labels are assumed.",
        mandatory=False,
        default=None,
    )
    add_interpolator = traits.Bool(
        desc="If True and mri is not None, then an interpolation matrix will be produced",
        mandatory=False,
        default=True,
        requires=["mri"],
    )
    sphere_units = traits.Enum(
        "m", "mm", desc="Defaults to 'm'.", mandatory=False, default="m"
    )
    single_volume = traits.Bool(
        desc="If True, multiple values of volume_label will be merged into a a single source space instead of occupying multiple source spaces (one for each sub-volume), i.e., len(src) will be 1 instead of len(volume_label). This can help conserve memory and disk space when many labels are used.",
        mandatory=False,
        default=False,
        requires=["volume_label"],
    )
    n_jobs = traits.Enum(
        1,
        2,
        desc="The number of jobs to run in parallel (default 1). Requires the joblib package. Will use at most 2 jobs (one for each hemisphere).",
        mandatory=False,
        default=1,
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class SetupVolumeSourceSpaceOutputSpec(TraitedSpec):
    src = File(desc="The resulting source space.", exists=True)


class SetupVolumeSourceSpace(BaseInterface):
    input_spec = SetupVolumeSourceSpaceInputSpec
    output_spec = SetupVolumeSourceSpaceOutputSpec

    def _run_interface(self, runtime):
        inputs = {
            "pos": 5.0,
            "mri": None,
            "sphere": None,
            "bem": None,
            "surface": None,
            "mindist": 5.0,
            "exclude": 0.0,
            "volume_label": None,
            "add_interpolator": True,
            "sphere_units": "m",
            "n_jobs": 1,
            "single_volume": False,
            "overwrite": False,
            "verbose": None,
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fname = inputs["fname"]
        subject = inputs["subject"]
        subjects_dir = inputs["subjects_dir"]
        pos = inputs["pos"]
        mri = inputs["mri"]
        sphere = inputs["sphere"]
        bem = inputs["bem"]
        surface = inputs["surface"]
        mindist = inputs["mindist"]
        exclude = inputs["exclude"]
        volume_label = inputs["volume_label"]
        add_interpolator = inputs["add_interpolator"]
        sphere_units = inputs["sphere_units"]
        single_volume = inputs["single_volume"]
        n_jobs = inputs["n_jobs"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        src = mne.setup_volume_source_space(
            subject=subject,
            pos=pos,
            mri=mri,
            sphere=sphere,
            bem=bem,
            surface=surface,
            mindist=mindist,
            exclude=exclude,
            subjects_dir=subjects_dir,
            volume_label=volume_label,
            add_interpolator=add_interpolator,
            sphere_units=sphere_units,
            single_volume=single_volume,
            n_jobs=n_jobs,
            verbose=verbose,
        )

        cwd = os.getcwd()
        fname = os.path.join(cwd, fname)
        src.save(fname, overwrite=overwrite)
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()

        cwd = os.getcwd()
        fname = self.inputs.fname
        fname = os.path.join(cwd, fname)
        outputs["src"] = fname
        return outputs


class CombineSourceSpacesInputSpec(BaseInterfaceInputSpec):
    fname = traits.File(
        desc="Output file name. Use a name <dir>/<name>-src.fif.", mandatory=True
    )
    sources = traits.List(
        traits.File(exists=True), minlen=2, desc="List of source files.", mandatory=True
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class CombineSourceSpacesOutputSpec(TraitedSpec):
    src = File(desc="The combined sources.", exists=True)


class CombineSourceSpaces(BaseInterface):
    input_spec = CombineSourceSpacesInputSpec
    output_spec = CombineSourceSpacesOutputSpec

    def _run_interface(self, runtime):
        inputs = {"overwrite": False, "verbose": None}
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fname = inputs["fname"]
        sources = inputs["sources"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        # Read sources
        srcs = [mne.read_source_spaces(fname) for fname in sources]
        # Combine sources
        src = srcs[0]
        for src_ in srcs[1:]:
            src += src_
        # Save
        cwd = os.getcwd()
        fname = os.path.join(cwd, fname)
        src.save(fname, overwrite=overwrite, verbose=verbose)
        return runtime

    def _list_outputs(self):
        fname = self.inputs.fname
        outputs = self.output_spec().get()
        cwd = os.getcwd()
        fname = os.path.join(cwd, fname)
        outputs["src"] = fname
        return outputs
