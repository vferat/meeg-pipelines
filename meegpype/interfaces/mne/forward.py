import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    File,
    TraitedSpec,
    isdefined,
)
import mne


class MakeForwardSolutionInputSpec(BaseInterfaceInputSpec):
    fname = traits.File(
        desc="Output file name. Use a name <dir>/<name>-fwd.fif.", mandatory=True
    )
    info = traits.File(
        desc="Path to a file with measurement information.", exists=True, mandatory=True
    )
    trans = traits.Union(
        traits.File(exists=True),
        traits.Enum("fsaverage", None),
        desc="The path to the head<->MRI transform *-trans.fif file produced during coregistration. Can also be 'fsaverage' to use the built-in fsaverage transformation. If trans is None, an identity matrix is assumed.",
        mandatory=True,
    )
    src = traits.File(
        desc="A path to a source space file.", exists=True, mandatory=True
    )
    bem = traits.File(desc="Filename of the BEM.", exists=True, mandatory=True)
    meg = traits.Bool(
        desc="If True (default), include MEG computations.",
        mandatory=False,
        default=True,
    )
    eeg = traits.Bool(
        desc="If True (default), include EEG computations.",
        mandatory=False,
        default=True,
    )
    mindist = traits.Float(
        desc="Minimum distance of sources from inner skull surface (in mm).",
        units="mm",
        mandatory=False,
        default=0.0,
    )
    ignore_ref = traits.Bool(
        desc="If True, do not include reference channels in compensation. This option should be True for KIT files, since forward computation with reference channels is not currently supported.",
        mandatory=False,
        default=False,
    )
    n_jobs = traits.Int(
        desc="The number of jobs to run in parallel. If -1, it is set to the number of CPU cores.",
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


class MakeForwardSolutionOutputSpec(TraitedSpec):
    forward = File(desc="The forward solution.", exists=True)


class MakeForwardSolution(BaseInterface):
    input_spec = MakeForwardSolutionInputSpec
    output_spec = MakeForwardSolutionOutputSpec

    def _run_interface(self, runtime):
        inputs = {
            "meg": True,
            "eeg": True,
            "mindist": 0.0,
            "ignore_ref": False,
            "n_jobs": 1,
            "overwrite": False,
            "verbose": None,
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fname = inputs["fname"]
        info = inputs["info"]
        trans = inputs["trans"]
        bem = inputs["bem"]
        src = inputs["src"]
        meg = inputs["meg"]
        eeg = inputs["eeg"]
        mindist = inputs["mindist"]
        ignore_ref = inputs["ignore_ref"]
        n_jobs = inputs["n_jobs"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        fwd = mne.make_forward_solution(
            info,
            trans,
            src,
            bem,
            meg=meg,
            eeg=eeg,
            mindist=mindist,
            ignore_ref=ignore_ref,
            n_jobs=n_jobs,
            verbose=verbose,
        )

        cwd = os.getcwd()
        fname = os.path.join(cwd, fname)
        fwd.save(fname, overwrite=overwrite)
        return runtime

    def _list_outputs(self):
        fname = self.inputs.fname
        outputs = self.output_spec().get()
        cwd = os.getcwd()
        fname = os.path.join(cwd, fname)
        outputs["forward"] = fname
        return outputs
