from nipype import Node, Workflow, IdentityInterface, MapNode
from meegpype.interfaces.mne import ComputeDestination
from meegpype.interfaces.mne import FilterChpi
from meegpype.interfaces.mne import ApplyMaxwellFilter
from meegpype.interfaces.mne import ComputeHeadPos


def init_maxwell_wf(name="maxwell_workflow", base_dir=None):

    wf = Workflow(name=name, base_dir=base_dir)

    # Nodes
    ## Inputs
    inputnode = Node(interface=IdentityInterface(fields=["raws", "emptyrooms", "crosstalks", "calibrations"]), name="inputnode")

    ## Processing
    compute_head_pos = MapNode(
        ComputeHeadPos(), iterfield=["raw", "emptyroom", "crosstalk", "calibration"], name="compute_head_pos"
    )
    compute_head_pos.inputs.rotation_velocity_limit = 1
    compute_head_pos.inputs.translation_velocity_limit = 0.01

    filter_chpi = MapNode(
        interface=FilterChpi(),
        iterfield=["raw"],
        name="filter_chpi",
    )
    filter_chpi.inputs.include_line = True
    filter_chpi.inputs.allow_line_only = True
    
    compute_destination = Node(
        interface=ComputeDestination(),
        joinsource="compute_head_pos",
        joinfield=["in_files", "head_positions"],
        unique=True,
        name="compute_destination",
    )

    wf.connect(inputnode, "raws", compute_head_pos, "raw")
    wf.connect(inputnode, "emptyrooms", compute_head_pos, "emptyroom")
    wf.connect(inputnode, "crosstalks", compute_head_pos, "crosstalk")
    wf.connect(inputnode, "calibrations", compute_head_pos, "calibration")
    wf.connect(
        [
            (
                compute_head_pos,
                compute_destination,
                [("raw", "in_files"), ("head_positions", "head_positions")],
            )
        ]
    )
    wf.connect(compute_head_pos, "raw", filter_chpi, "raw")

    compute_maxwell = MapNode(
        ApplyMaxwellFilter(),
        iterfield=["raw", "head_positions", "emptyroom", "crosstalk", "calibration"],
        name="compute_maxwell",
        mem_gb=10,
    )


    wf.connect(compute_destination, "destination", compute_maxwell, "destination")

    wf.connect(filter_chpi, "raw", compute_maxwell, "raw")

    wf.connect(
        compute_head_pos, "head_positions", compute_maxwell, "head_positions"
    )
    wf.connect(
        compute_head_pos, "emptyroom", compute_maxwell, "emptyroom"
    )
    wf.connect(
        compute_head_pos, "crosstalk", compute_maxwell, "crosstalk"
    )
    wf.connect(
        compute_head_pos, "calibration", compute_maxwell, "calibration"
        )
    
    # TODO: rename emptyroom

    ## Outputs
    outputnode = Node(
        interface=IdentityInterface(fields=["info", "destination", "raw_tsss", "raw_tsss_splits", "emptyroom_tsss", "emptyroom_tsss_splits", "head_positions"]),
        name="outputnode",
    )
    wf.connect(compute_destination, "info", outputnode, "info")
    wf.connect(compute_destination, "destination", outputnode, "destination")
    wf.connect(compute_maxwell, "raw_tsss", outputnode, "raw_tsss")
    wf.connect(compute_maxwell, "raw_tsss_splits", outputnode, "raw_tsss_splits")
    wf.connect(compute_maxwell, "emptyroom_tsss", outputnode, "emptyroom_tsss")
    wf.connect(compute_maxwell, "emptyroom_tsss_splits", outputnode, "emptyroom_tsss_splits")
    wf.connect(compute_head_pos, "head_positions", outputnode, "head_positions")
    return wf



