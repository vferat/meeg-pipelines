import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    File,
    TraitedSpec,
    isdefined,
    Directory,
)
import mne
from mne.preprocessing import annotate_movement



class FilterChpiInputSpec(BaseInterfaceInputSpec):
    raw = traits.Either(
        File(exists=True),
        Directory(exists=True),
        desc="The input raw file.",
        mandatory=True,
    )
    include_line = traits.Bool(
        default=True,
        desc="If True, also filter line noise.",
    )
    t_step = traits.Float(
        default=0.01,
        desc="Time step to use for estimation, default is 0.01 (10 ms).",
    )
    t_window = traits.Float(
        default='auto',
        desc="Time window to use to estimate the amplitudes, default is 0.2 (200 ms).",
    )
    ext_order = traits.Int(
        desc="The external order for SSS-like interfence suppression. The SSS bases are used as projection vectors during fitting.",
    )
    allow_line_only = traits.Bool(
        desc="If True, allow filtering line noise only. The default is False, which only allows the function to run when cHPI information is present.",
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class FilterChpiOutputSpec(TraitedSpec):
    raw = File(desc="The raw file.", exists=True)
    splits = traits.List(File(desc="List of generated raw files.", exists=True))


class FilterChpi(BaseInterface):
    input_spec = FilterChpiInputSpec
    output_spec = FilterChpiOutputSpec

    def _run_interface(self, runtime):

        inputs = {"include_line": True, "t_step": 0.01, "t_window": 'auto', "ext_order": 1, "allow_line_only": False, "overwrite": False, "verbose": None}
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        raw_path = inputs["raw"]
        include_line = inputs["include_line"]
        t_step = inputs["t_step"]
        t_window = inputs["t_window"]
        ext_order = inputs["ext_order"]
        allow_line_only = inputs["allow_line_only"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        # Create output names
        raw_basename = os.path.basename(raw_path)
        cwd = os.getcwd()
        self.output_raw_path = os.path.join(cwd, f"filtered_{raw_basename}")

        # Load raw data
        raw = mne.io.read_raw(raw_path, allow_maxshield="yes", preload=True)
        # Compute head positions
        raw_chpi = mne.chpi.filter_chpi(
            raw,
            include_line=include_line,
            t_step=t_step,
            t_window=t_window,
            ext_order=ext_order,
            allow_line_only=allow_line_only,
            verbose=verbose
        )
        self.splits = raw_chpi.save(self.output_raw_path, overwrite=overwrite)
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["raw"] = self.output_raw_path
        outputs["splits"] = self.splits
        return outputs
