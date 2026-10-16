import os

import numpy as np
from nipype.interfaces.base import (
    BaseInterface,
    BaseInterfaceInputSpec,
    traits,
    TraitedSpec,
)


class FitSurfaceToMaskInputSpec(BaseInterfaceInputSpec):
    in_mask = traits.File(
        desc="The path to a binary mask volume (any non-zero voxel is in the mask).",
        exists=True,
        mandatory=True,
    )
    in_reference = traits.File(
        desc="The path to a FreeSurfer volume of the subject (e.g. T1.mgz), used to "
        "express the surface in FreeSurfer surface RAS coordinates.",
        exists=True,
        mandatory=True,
    )
    output_surface = traits.File(
        desc="The path to the output surface mesh.",
        mandatory=True,
    )
    offset = traits.Float(
        0.0,
        usedefault=True,
        desc="Distance (mm) between the mask boundary and the fitted surface. "
        "Positive values place the surface outside the mask.",
    )
    ico = traits.Int(
        4,
        usedefault=True,
        desc="Subdivision of the icosahedron used as template (4 = 5120 triangles).",
    )
    n_iterations = traits.Int(
        1000,
        usedefault=True,
        desc="Maximum number of deformation iterations.",
    )


class FitSurfaceToMaskOutputSpec(TraitedSpec):
    output_surface = traits.File(
        desc="The path to the output surface mesh.",
        exists=True,
    )


class FitSurfaceToMask(BaseInterface):
    """Fit a deformable spherical template to the boundary of a mask.

    An icosahedron enclosing the mask is shrunk until it reaches the iso-surface of
    the signed distance to the mask at ``offset`` mm, while a smoothing term keeps
    the mesh regular. The surface keeps the topology of MNE's icosahedron, so it can
    be used directly with ``mne.make_bem_model(ico=...)``.
    """

    input_spec = FitSurfaceToMaskInputSpec
    output_spec = FitSurfaceToMaskOutputSpec

    def _run_interface(self, runtime):
        import mne

        rr, tris, volume_info = fit_surface_to_mask(
            self.inputs.in_mask,
            self.inputs.in_reference,
            offset=self.inputs.offset,
            ico=self.inputs.ico,
            n_iterations=self.inputs.n_iterations,
        )
        mne.write_surface(
            os.path.abspath(self.inputs.output_surface),
            rr,
            tris,
            volume_info=volume_info,
            overwrite=True,
        )
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["output_surface"] = os.path.abspath(self.inputs.output_surface)
        return outputs


def fit_surface_to_mask(in_mask, in_reference, offset=0.0, ico=4, n_iterations=1000):
    """Fit an icosahedral surface to the iso-surface at ``offset`` mm of a mask.

    Returns the vertices (FreeSurfer surface RAS, mm), the triangles and the volume
    info of the reference volume.
    """
    import nibabel as nib
    from scipy import ndimage, sparse
    from mne.surface import _get_ico_surface

    # Mask: keep the largest connected component and fill its holes
    mask_img = nib.load(in_mask)
    mask = np.asanyarray(mask_img.dataobj) > 0
    labels, n_labels = ndimage.label(mask)
    if n_labels == 0:
        raise ValueError(f"The mask {in_mask} is empty.")
    mask = labels == np.argmax(np.bincount(labels.ravel())[1:]) + 1
    mask = ndimage.binary_fill_holes(mask)

    # Signed distance to the mask boundary (mm): positive outside, negative inside
    zooms = mask_img.header.get_zooms()[:3]
    sdist = ndimage.distance_transform_edt(~mask, sampling=zooms) - ndimage.distance_transform_edt(
        mask, sampling=zooms
    )

    # Mask voxels -> FreeSurfer surface RAS (tkr)
    ref_img = nib.load(in_reference)
    vox2tkr = ref_img.header.get_vox2ras_tkr() @ np.linalg.inv(ref_img.affine) @ mask_img.affine
    tkr2vox = np.linalg.inv(vox2tkr)

    def sample(points):
        vox = points @ tkr2vox[:3, :3].T + tkr2vox[:3, 3]
        return ndimage.map_coordinates(sdist, vox.T, order=1, mode="nearest")

    # Template: MNE's icosahedron (its triangle ordering is required by make_bem_model)
    surf = _get_ico_surface(ico)
    tris = surf["tris"]
    unit = surf["rr"] / np.linalg.norm(surf["rr"], axis=1, keepdims=True)
    mask_rr = np.argwhere(mask) @ vox2tkr[:3, :3].T + vox2tkr[:3, 3]
    center = mask_rr.mean(axis=0)
    radius = np.linalg.norm(mask_rr - center, axis=1).max() + max(offset, 0) + 10
    rr = center + radius * unit

    # Mean of the neighbors of each vertex
    edges = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    adjacency = sparse.coo_matrix(
        (np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(len(rr), len(rr))
    ).tocsr()
    adjacency = ((adjacency + adjacency.T) > 0).astype(float)
    adjacency = sparse.diags(1.0 / np.asarray(adjacency.sum(axis=1)).ravel()) @ adjacency

    def normals(points):
        tri_nn = np.cross(points[tris[:, 1]] - points[tris[:, 0]], points[tris[:, 2]] - points[tris[:, 0]])
        nn = np.zeros_like(points)
        for k in range(3):
            np.add.at(nn, tris[:, k], tri_nn)
        return nn / np.linalg.norm(nn, axis=1, keepdims=True)

    # Orient the normals outward
    orientation = np.sign(np.sum(normals(rr) * unit))

    # Deformation: move each vertex along its normal toward the iso-surface, smooth
    # the mesh tangentially (keeps it regular) and slightly along the normal.
    step, max_step = 0.5, 1.0  # mm
    tangential_smoothing, normal_smoothing = 0.5, 0.05
    for _ in range(n_iterations):
        nn = orientation * normals(rr)
        force = np.clip(sample(rr) - offset, -max_step, max_step)
        lap = adjacency @ rr - rr
        lap_n = np.sum(lap * nn, axis=1, keepdims=True) * nn
        move = tangential_smoothing * (lap - lap_n) + normal_smoothing * lap_n - step * force[:, None] * nn
        rr = rr + move
        if np.abs(move).max() < 1e-3:
            break

    return rr, tris, _volume_info(in_reference)


def _volume_info(mgz):
    """Volume info of a FreeSurfer volume, as stored in surface files."""
    import nibabel as nib

    header = nib.load(mgz).header
    if not isinstance(header, nib.freesurfer.mghformat.MGHHeader) or header["version"] != 1:
        return None
    return dict(
        head=np.array([2, 0, 20]),
        valid="1  # volume info valid",
        filename=mgz,
        volume=header["dims"][:3],
        voxelsize=header["delta"],
        xras=header["Mdc"][0],
        yras=header["Mdc"][1],
        zras=header["Mdc"][2],
        cras=header["Pxyz_c"],
    )
