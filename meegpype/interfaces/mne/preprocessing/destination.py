import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    File,
    TraitedSpec,
)
import mne
from mne.preprocessing import compute_average_dev_head_t


class ComputeDestinationInputSpec(BaseInterfaceInputSpec):
    in_files = traits.List(
        File(exists=True), desc="List of input files to be processed.", mandatory=True
    )
    head_positions = traits.List(
        File(exists=True), desc="List of head positions.", mandatory=True
    )


class ComputeDestinationOutputSpec(TraitedSpec):
    destination = traits.File(exists=True, desc="The average device to head transform.")
    info = traits.File(
        exists=True, desc="The info with the new device to head transform."
    )


class ComputeDestination(BaseInterface):
    input_spec = ComputeDestinationInputSpec
    output_spec = ComputeDestinationOutputSpec

    def _run_interface(self, runtime):
        raws = self.inputs.in_files
        raws = [mne.io.read_raw(f, allow_maxshield="yes") for f in raws]
        head_positions = self.inputs.head_positions

        # Compute destination
        head_positions = [mne.chpi.read_head_pos(hp) for hp in head_positions]
        dev_head_t = compute_average_dev_head_t(raws, pos=head_positions)
        destination_path = os.path.join(os.getcwd(), "destination-trans.fif")
        dev_head_t.save(destination_path)
        self.destination = destination_path

        # Update info
        info = raws[0].info
        info["dev_head_t"] = dev_head_t
        info_path = os.path.join(os.getcwd(), "destination-info.fif")
        self.info = info_path
        info.save(info_path)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["destination"] = self.destination
        outputs["info"] = self.info
        return outputs
