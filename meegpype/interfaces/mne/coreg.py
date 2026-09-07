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


class MakeCoregInputSpec(BaseInterfaceInputSpec):
    fname = traits.File(
        desc="Output file name. Use a name <dir>/<name>-trans.fif.", mandatory=True
    )
    subject = traits.Str(desc="Subject name (required)", mandatory=True)
    subjects_dir = Directory(desc="Subjects directory", exists=True, mandatory=True)
    info = traits.File(
        desc="Path to a file with measurement information.", exists=True, mandatory=True
    )
    fiducials = traits.File(
        exists=True,
        desc="File path to fif file containing the fiducials."
        "If' no set, the fiducials are derived from the fsaverage template.",
        mandatory=False,
    )
    lpa_weight = traits.Float(
        desc="Relative weight for LPA. The default value is 1.",
        mandatory=False,
        default=1,
    )
    nasion_weight = traits.Float(
        desc="Relative weight for nation. The default value is 10.",
        mandatory=False,
        default=10,
    )
    rpa_weight = traits.Float(
        desc="Relative weight for RPA. The default value is 1.",
        mandatory=False,
        default=1,
    )
    hsp_weight = traits.Float(
        desc="Relative weight for HSP. The default value is 1.",
        mandatory=False,
        default=1,
    )
    eeg_weight = traits.Float(
        desc="Relative weight for EEG. The default value is 1.",
        mandatory=False,
        default=1,
    )
    hpi_weight = traits.Float(
        desc="Relative weight for HPI. The default value is 1.",
        mandatory=False,
        default=1,
    )
    n_iterations = traits.Int(
        desc="Maximum number of iterations for ICP fitting.", mandatory=False
    )
    distance = traits.Float(
        desc="Exclude all points that are further away from the MRI head than this distance (in m.)"
        "A value of distance <= 0 excludes nothing.",
        mandatory=False,
        default=10,
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class MakeCoregOutputSpec(TraitedSpec):
    trans = File(desc="The trans file.", exists=True)


class MakeCoreg(BaseInterface):
    input_spec = MakeCoregInputSpec
    output_spec = MakeCoregOutputSpec

    def _run_interface(self, runtime):
        inputs = {
            "fiducials": "estimated",
            "n_iterations": 20,
            "lpa_weight": 1,
            "nasion_weight": 10,
            "rpa_weight": 1,
            "hsp_weight": 1,
            "eeg_weight": 1,
            "hpi_weight": 1,
            "distance": 0,
            "overwrite": False,
            "verbose": None,
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fname = inputs["fname"]
        subject = inputs["subject"]
        subjects_dir = inputs["subjects_dir"]
        info = inputs["info"]
        fiducials = inputs["fiducials"]
        if fiducials != "estimated":
            fiducials, coord_frame = mne.io.read_fiducials(fiducials)
        n_iterations = inputs["n_iterations"]
        lpa_weight = inputs["lpa_weight"]
        nasion_weight = inputs["nasion_weight"]
        rpa_weight = inputs["rpa_weight"]
        hsp_weight = inputs["hsp_weight"]
        eeg_weight = inputs["eeg_weight"]
        hpi_weight = inputs["hpi_weight"]
        distance = inputs["distance"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        # Read info
        info = mne.io.read_info(info)
        # Coregistration
        coreg = mne.coreg.Coregistration(
            info=info, subject=subject, subjects_dir=subjects_dir, fiducials=fiducials
        )
        coreg.fit_fiducials(verbose=verbose)
        coreg.fit_icp(
            n_iterations=n_iterations,
            lpa_weight=lpa_weight,
            nasion_weight=nasion_weight,
            rpa_weight=rpa_weight,
            hsp_weight=hsp_weight,
            eeg_weight=eeg_weight,
            hpi_weight=hpi_weight,
            verbose=verbose,
        )
        coreg.omit_head_shape_points(distance=distance)
        coreg.fit_icp(
            n_iterations=n_iterations,
            lpa_weight=lpa_weight,
            nasion_weight=nasion_weight,
            rpa_weight=rpa_weight,
            hsp_weight=hsp_weight,
            eeg_weight=eeg_weight,
            hpi_weight=hpi_weight,
            verbose=verbose,
        )
        # Save
        cwd = os.getcwd()
        self.fname = os.path.join(cwd, fname)
        mne.write_trans(fname, coreg.trans, overwrite=overwrite)
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["trans"] =  self.fname
        return outputs
