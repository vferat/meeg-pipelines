import os
import numpy as np
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
import mne_bids


class ApplyMaxwellFilterInputSpec(BaseInterfaceInputSpec):
    raw = traits.Either(
        File(exists=True),
        Directory(exists=True),
        desc="Input file name.",
        mandatory=True)
    head_positions = traits.File(exists=True,
                                desc="The head positions.",
                                mandatory=True)
    destination = File(exists=True,
                       desc="The destination device to head transform.",
                       mandatory=True)
    emptyroom = traits.Either(
        File(exists=True),
        Directory(exists=True),
        None,
        desc="emptyroom recording.",
        mandatory=False)
    calibration = traits.Either(traits.File(exists=True), None,
                                desc="The calibration file.",
                                mandatory=False)
    crosstalk = traits.Either(traits.File(exists=True), None,
                              desc="The cross talk file.",
                              mandatory=False)
    st_duration = traits.Float(desc="The st_duration.", mandatory=False)


class ApplyMaxwellFilterOutputSpec(TraitedSpec):
    raw_tsss = File(exists=True, desc="The raw file after Maxwell filtering.")
    raw_tsss_splits = traits.List(traits.File(exists=True))
    emptyroom_tsss = traits.Either(File(exists=True), None,
                                   desc="The emptyroom file after Maxwell filtering.")
    emptyroom_tsss_splits = traits.Either(traits.List(traits.File(exists=True)), None)


class ApplyMaxwellFilter(BaseInterface):
    input_spec = ApplyMaxwellFilterInputSpec
    output_spec = ApplyMaxwellFilterOutputSpec

    def _run_interface(self, runtime):

        inputs = {"st_duration": 30}
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value
        st_duration = inputs["st_duration"]

        raw = mne.io.read_raw(self.inputs.raw, allow_maxshield="yes")
        destination = mne.read_trans(self.inputs.destination)
        head_positions = mne.chpi.read_head_pos(self.inputs.head_positions)

        if isdefined(self.inputs.calibration):
            calibration = self.inputs.calibration
        else:
            calibration = None

        if isdefined(self.inputs.crosstalk):
            cross_talk = self.inputs.crosstalk
        else:
            cross_talk = None

        if isdefined(self.inputs.emptyroom):
            emptyroom = self.inputs.emptyroom
        else:
            emptyroom = None

        # general parameters
        ignore_ref = True
        origin = "auto"
        int_order = 8
        ext_order = 3
        bad_condition = "error"
        coord_frame = "head"
        regularize = "in"
        skip_by_annotation = ("edge", "bad_acq_skip")
        mag_scale = 100.0
        h_freq = 40.0

        extended_proj = ()
        if emptyroom:
            emptyroom = mne.io.read_raw(emptyroom, allow_maxshield="yes")
            extended_proj = mne.compute_proj_raw(
                emptyroom,
                n_grad=3,
                n_mag=3,
                meg="combined",
            )

        noisy_chs, flat_chs = mne.preprocessing.find_bad_channels_maxwell(
            raw,
            limit=7.0,
            duration=5.0,
            min_count=5,
            return_scores=False,
            origin=origin,
            int_order=int_order,
            ext_order=ext_order,
            calibration=calibration,
            cross_talk=cross_talk,
            coord_frame=coord_frame,
            regularize=regularize,
            ignore_ref=ignore_ref,
            bad_condition=bad_condition,
            head_pos=head_positions,
            mag_scale=mag_scale,
            skip_by_annotation=skip_by_annotation,
            h_freq=h_freq,
            extended_proj=extended_proj,
            verbose=None,
        )


        all_bads = np.unique(raw.info["bads"] + noisy_chs + flat_chs).tolist()
        raw.info["bads"] = all_bads
    
        st_correlation = 0.98
        maxwell_filter_args = {
            "origin": origin,
            "int_order": int_order,
            "ext_order": ext_order,
            "calibration": calibration,
            "cross_talk": cross_talk,
            "coord_frame": coord_frame,
            "regularize": regularize,
            "ignore_ref": ignore_ref,
            "bad_condition": bad_condition,
            "head_pos": head_positions,
            "mag_scale": mag_scale,
            "skip_by_annotation": skip_by_annotation,
            "extended_proj": extended_proj,
            "st_duration": st_duration,
            "st_correlation": st_correlation,
            "destination": destination,
        }


        raw_tsss = mne.preprocessing.maxwell_filter(raw, **maxwell_filter_args)

        cwd = os.getcwd()
        raw_basename = os.path.basename(self.inputs.raw)
        raw_bidspath = mne_bids.get_bids_path_from_fname(raw_basename)

        raw_tsss_bidspath = raw_bidspath.copy().update(processing="tsss")
        self.raw_tsss_path = os.path.join(cwd, raw_tsss_bidspath.basename)
        self.raw_tsss_splits = raw_tsss.save(self.raw_tsss_path, overwrite=True)

        if emptyroom:
            emptyroom = mne.preprocessing.maxwell_filter_prepare_emptyroom(emptyroom, raw=raw)
            emptyroom_tsss = mne.preprocessing.maxwell_filter(emptyroom, **maxwell_filter_args)

            emptyroom_bidspath =  raw_tsss_bidspath.copy().update(subject="er")
            self.emptyroom_tsss_path = os.path.join(cwd, emptyroom_bidspath.basename)
            self.emptyroom_tsss_splits = emptyroom_tsss.save(self.emptyroom_tsss_path, overwrite=True)
        else:
            self.emptyroom_tsss_path = None
            self.emptyroom_tsss_splits = None

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["raw_tsss"] = self.raw_tsss_path
        outputs["raw_tsss_splits"] = self.raw_tsss_splits

        if self.emptyroom_tsss_path:
            outputs["emptyroom_tsss"] = self.emptyroom_tsss_path
            outputs["emptyroom_tsss_splits"] = self.emptyroom_tsss_splits
        return outputs
