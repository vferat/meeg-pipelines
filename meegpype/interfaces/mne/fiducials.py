import os
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    File,
    TraitedSpec,
    isdefined,
)
import numpy as np
import nibabel as nib
from nibabel.affines import apply_affine
import mne
from mne._fiff.constants import FIFF


def parse_lta(file_path):
    with open(file_path) as file:
        lines = file.readlines()

    # Find the section that starts with '1 4 4' (the transformation matrix section)
    matrix_start = False
    matrix = []
    for line in lines:
        if matrix_start:
            matrix.append([float(num) for num in line.split()])
            if len(matrix) == 4:
                break
        if line.startswith("1 4 4"):
            matrix_start = True

    return np.array(matrix)


class ApplyTransformInputSpec(BaseInterfaceInputSpec):
    fiducials = traits.Dict(
        desc="The fiducials file in T1w voxel space.", mandatory=True
    )
    vox2vox = traits.File(
        desc="The voxel to voxel lta transform from T1w to fsnative space.",
        mandatory=True,
    )
    fsnative = traits.File(
        desc="The target image file in which fiducials will be defined (RAS surface).",
        mandatory=True,
    )


class ApplyTransformOutputSpec(TraitedSpec):
    fiducials = File(
        desc="The fiducial .fif file in fsnative surface RAS space (m).", exists=True
    )


class ApplyTransform(BaseInterface):
    input_spec = ApplyTransformInputSpec
    output_spec = ApplyTransformOutputSpec

    def _run_interface(self, runtime):
        inputs = {}
        for key, value in self.inputs.get().items():
            if isdefined(getattr(self.inputs, key)):
                inputs[key] = value

        fiducials = inputs["fiducials"]
        vox2vox = inputs["vox2vox"]
        fsnative = inputs["fsnative"]

        # Read files
        vox2vox_transform = parse_lta(vox2vox)
        vox2ras_tkr_transform = nib.load(fsnative).header.get_vox2ras_tkr()

        # Compute transformation. The fiducials must be tranform to surface RAS coordinate system
        full_transform = vox2ras_tkr_transform.dot(vox2vox_transform)

        # Apply transformation to fiducials
        pts = []
        for fiducial_name, coord in fiducials.items():
            coord = apply_affine(full_transform, coord) * 1e-3
            if fiducial_name.lower() in ["nas", "nasion"]:
                pt = dict(kind=FIFF.FIFFV_POINT_CARDINAL, r=coord, ident=2)
                pts.append(pt)
            elif fiducial_name.lower() == "lpa":
                pt = dict(kind=FIFF.FIFFV_POINT_CARDINAL, r=coord, ident=1)
                pts.append(pt)
            elif fiducial_name.lower() == "rpa":
                pt = dict(kind=FIFF.FIFFV_POINT_CARDINAL, r=coord, ident=3)
                pts.append(pt)
            else:
                pass

        # Save
        cwd = os.getcwd()
        self.fname = os.path.join(cwd, "fiducials.fif")
        mne.io.write_fiducials(
            self.fname, pts, coord_frame="mri_voxel", overwrite=False, verbose=None
        )
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["fiducials"] = self.fname
        return outputs
