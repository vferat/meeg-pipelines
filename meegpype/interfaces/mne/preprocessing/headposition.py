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


class ComputeHeadPosInputSpec(BaseInterfaceInputSpec):
    raw = traits.Either(
        File(exists=True),
        Directory(exists=True),
        desc="The input raw file.",
        mandatory=True,
    )
    rotation_velocity_limit = traits.Float(
        desc="Head rotation velocity limit in degrees per second.",
    )
    translation_velocity_limit = traits.Float(
        desc="Head translation velocity limit in meters per second.",
    )
    emptyroom = traits.Either(
        File(exists=True),
        Directory(exists=True),
        None,
        desc="The emptyroom associated to the raw file. (no used)",
    )
    crosstalk = traits.Either(
        File(exists=True),
        None,
        desc="The crosstalk associated to the raw file. (no used)",
    )
    calibration = traits.Either(
        File(exists=True),
        None,
        desc="The calibration associated to the raw file. (no used)",
    )
    overwrite = traits.Bool(
        desc="Overwrite existing files.", mandatory=False, default=False
    )
    verbose = traits.Bool(
        desc="Enable verbose mode (printing of log messages).",
        mandatory=False,
        default=None,
    )


class ComputeHeadPosOutputSpec(TraitedSpec):
    raw = File(desc="The raw file.", exists=True)
    splits = traits.List(File(desc="List of generated raw files.", exists=True))
    head_positions = File(
        desc="File containing the head postions in txt format.", exists=True
    )
    emptyroom = traits.Either(
                    File(exists=True),
                    None,
                    desc="The emptyroom associated to the raw file.")
    crosstalk = traits.Either(
                    File(exists=True),
                    None,
                    desc="The crosstalk associated to the raw file.")
    calibration = traits.Either(
                    File(exists=True),
                    None,
                    desc="The calibration associated to the raw file.")


class ComputeHeadPos(BaseInterface):
    input_spec = ComputeHeadPosInputSpec
    output_spec = ComputeHeadPosOutputSpec

    def _run_interface(self, runtime):

        inputs = {
            "rotation_velocity_limit": None,
            "translation_velocity_limit": None,
            "emptyroom": None,
            "crosstalk": None,
            "calibration": None,
            "overwrite": False,
            "verbose": None
        }
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        raw_path = inputs["raw"]
        rotation_velocity_limit = inputs["rotation_velocity_limit"]
        translation_velocity_limit = inputs["translation_velocity_limit"]
        emptyroom_path = inputs["emptyroom"]
        crosstalk_path = inputs["crosstalk"]
        calibration_path = inputs["calibration"]
        overwrite = inputs["overwrite"]
        verbose = inputs["verbose"]

        # Create output names
        raw_basename = os.path.basename(raw_path)
        headpos_basename = os.path.splitext(raw_basename)[0] + "_headpos.txt"

        # Load raw data
        raw = mne.io.read_raw(raw_path, allow_maxshield="yes")
        # Compute head positions
        if raw.info["hpi_meas"] and raw.info["hpi_subsystem"]:
            chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw, verbose=verbose)
            chpi_locs = mne.chpi.compute_chpi_locs(
                raw.info, chpi_amplitudes, verbose=verbose
            )
        else:
            chpi_locs = mne.chpi.extract_chpi_locs_ctf(raw, verbose=verbose)

        head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs, verbose=verbose)

        # Annotate movement
        annotations, _ = mne.preprocessing.annotate_movement(raw,
                                            head_pos,
                                            rotation_velocity_limit=rotation_velocity_limit,
                                            translation_velocity_limit=translation_velocity_limit,
                                            mean_distance_limit=None,
                                            use_dev_head_trans='average')
        all_annotations = raw.annotations.copy() + annotations
        raw.set_annotations(all_annotations)

        # Save
        cwd = os.getcwd()
        self.output_raw_path = os.path.join(cwd, raw_basename)
        self.splits = raw.save(self.output_raw_path, overwrite=overwrite)

        self.output_headpos_path = os.path.join(cwd, headpos_basename)
        mne.chpi.write_head_pos(self.output_headpos_path, head_pos)

        self.emptyroom_path = emptyroom_path
        self.crosstalk_path = crosstalk_path
        self.calibration_path = calibration_path
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["head_positions"] = self.output_headpos_path
        outputs["raw"] = self.output_raw_path
        outputs["splits"] = self.splits
        outputs["emptyroom"] = self.emptyroom_path
        outputs["crosstalk"] = self.crosstalk_path
        outputs["calibration"] = self.calibration_path
        return outputs
