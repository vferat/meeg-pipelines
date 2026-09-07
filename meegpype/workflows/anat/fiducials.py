from nipype.interfaces.utility import IdentityInterface
from nipype import Node, Workflow
from nipype.interfaces.freesurfer import MRICoreg
from nipype.interfaces.io import FreeSurferSource
from meegpype.interfaces.mne import ApplyTransform


def init_fiducials_wf(name="fiducials", work_dir=None):
    # Initiate workflow
    wf = Workflow(name=name, base_dir=work_dir)

    # Nodes
    ## Inputs
    inputnode = Node(
        IdentityInterface(
            fields=["fiducials", "reference", "subject_id", "subjects_dir"],
            mandatory_inputs=True,
        ),
        name="inputnode",
    )

    fs_source = Node(FreeSurferSource(), name="fs_source")

    coreg = Node(MRICoreg(), name="coreg")

    ### Apply transformation
    apply_transform = Node(ApplyTransform(), name="apply_transform")

    ## Connections
    wf.connect(inputnode, "fiducials", apply_transform, "fiducials")
    wf.connect(inputnode, "reference", coreg, "source_file")

    wf.connect(inputnode, "subject_id", fs_source, "subject_id")
    wf.connect(inputnode, "subjects_dir", fs_source, "subjects_dir")

    wf.connect(fs_source, "T1", coreg, "reference_file")

    wf.connect(coreg, "out_lta_file", apply_transform, "vox2vox")
    wf.connect(fs_source, "T1", apply_transform, "fsnative")

    ## output
    outputnode = Node(
        interface=IdentityInterface(fields=["fiducials"]), name="outputnode"
    )
    wf.connect(apply_transform, "fiducials", outputnode, "fiducials")
    return wf
