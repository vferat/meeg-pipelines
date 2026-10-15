import numpy as np
import nibabel as nib
import mne
from scipy import ndimage

from ..fit_surface import FitSurfaceToMask


def _make_data(tmp_path):
    """Conformed reference volume and an ellipsoid mask, with their signed distance."""
    affine = np.array([[-1, 0, 0, 133], [0, 0, 1, -140], [0, -1, 0, 148], [0, 0, 0, 1.0]])
    reference = tmp_path / "T1.mgz"
    nib.save(nib.MGHImage(np.zeros((256,) * 3, np.uint8), affine), reference)

    vox2tkr = nib.load(reference).header.get_vox2ras_tkr()
    ijk = np.indices((256,) * 3).reshape(3, -1).T
    tkr = ijk @ vox2tkr[:3, :3].T + vox2tkr[:3, 3]
    mask = (np.sum(((tkr - [10, -5, 15]) / [70, 85, 60]) ** 2, axis=1) <= 1).reshape((256,) * 3)
    in_mask = tmp_path / "mask.nii.gz"
    nib.save(nib.Nifti1Image(mask.astype(np.uint8), affine), in_mask)

    sdist = ndimage.distance_transform_edt(~mask) - ndimage.distance_transform_edt(mask)
    tkr2vox = np.linalg.inv(vox2tkr)

    def distance(rr):
        vox = rr @ tkr2vox[:3, :3].T + tkr2vox[:3, 3]
        return ndimage.map_coordinates(sdist, vox.T, order=1)

    return in_mask, reference, distance


def test_fit_surface_to_mask(tmp_path):
    in_mask, reference, distance = _make_data(tmp_path)
    surfaces = dict()
    for name, offset in [("inner_skull", 4.0), ("outer_skull", 10.0), ("outer_skin", 16.0)]:
        fit = FitSurfaceToMask()
        fit.inputs.in_mask = str(in_mask)
        fit.inputs.in_reference = str(reference)
        fit.inputs.offset = offset
        fit.inputs.output_surface = str(tmp_path / f"{name}.surf")
        result = fit.run()
        rr, tris = mne.read_surface(result.outputs.output_surface)
        assert len(tris) == 5120
        assert np.abs(distance(rr) - offset).max() < 0.5
        surfaces[name] = (rr, tris)

    # The surfaces are usable as a BEM model, with MNE's icosahedron downsampling
    bem_dir = tmp_path / "subjects" / "fake" / "bem"
    bem_dir.mkdir(parents=True)
    for name, (rr, tris) in surfaces.items():
        mne.write_surface(bem_dir / f"{name}.surf", rr, tris)
    mne.make_bem_model(
        "fake", ico=4, conductivity=(0.3, 0.006, 0.3), subjects_dir=tmp_path / "subjects"
    )
