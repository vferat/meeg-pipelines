import os
from nipype.interfaces.fsl.maths import ApplyMask, Threshold
from nipype.interfaces.base import (
    TraitedSpec,
    File,
    traits
)
from nipype.interfaces.freesurfer.base import FSCommand, FSTraitedSpec
from nipype import Workflow, Node, IdentityInterface

os.environ["PATH"] += os.pathsep + '/opt/freesurfer/fsfast/bin'


class MkHeadSurfInputSpec(FSTraitedSpec):
    input_file = File(desc="File", exists=True, mandatory=True, argstr="-i %s")
    thresh1 = traits.Int(desc="threshold 1", mandatory=True, argstr="-thresh1 %s")
    thresh2 = traits.Int(desc="threshold 2", mandatory=True, argstr="-thresh2 %s")
    output_img = File(desc="File", exists=False, argstr="-o %s", name_source='input_file', name_template='%s_headmask.nii')
    output_surf = File(desc="File", exists=False, argstr="-surf %s", name_source='input_file', name_template='%s_headsurf')

class MkHeadSurfOutputSpec(TraitedSpec):
    output_img = File(desc="output image", exists=True)
    output_surf = File(desc="output surface", exists=True)


class MkHeadSurf(FSCommand):
    input_spec = MkHeadSurfInputSpec
    output_spec = MkHeadSurfOutputSpec
    _cmd = 'mkheadsurf'


inv2_path = r"/data/T1/_t1_mp2rage_sag_pTx_0.6_CS5_20241015131533_13.nii"
mp2rage_path =  r"/data/T1/_t1_mp2rage_sag_pTx_0.6_CS5_20241015131533_17.nii"

work_dir = '/data/mp2rage'
name = 'mp2rage'
wf = Workflow(name=name, base_dir=work_dir)

inputnode = Node(IdentityInterface(fields=['inv2', 'mp2rage']), name='inputnode')
inputnode.inputs.inv2 = inv2_path
inputnode.inputs.mp2rage = mp2rage_path

thresold_img = Node(Threshold(), name='thresold_img')
thresold_img.inputs.thresh = 140

apply_mask_1 = Node(ApplyMask(), name='apply_mask_1')

mkheadsurf =  Node(MkHeadSurf(), name='mkheadsurf')
mkheadsurf.inputs.thresh1 = 20
mkheadsurf.inputs.thresh2 = 20
mkheadsurf.inputs.environ = {'PATH': os.environ['PATH']}

apply_mask_2 = Node(ApplyMask(), name='apply_mask_2')

outputnode = Node(IdentityInterface(fields=['inv2', 'mp2rage']), name='outputnode')
outputnode.inputs.mp2rage = inv2_path
outputnode.inputs.headmask = mp2rage_path
outputnode.inputs.headsurf = mp2rage_path


wf.connect(inputnode, 'inv2', thresold_img, 'in_file')
wf.connect(inputnode, 'mp2rage', apply_mask_1, 'in_file')

wf.connect(thresold_img, 'out_file', apply_mask_1, 'mask_file')
wf.connect(apply_mask_1, 'out_file', mkheadsurf, 'input_file')

wf.connect(inputnode, 'mp2rage', apply_mask_2, 'in_file')
wf.connect(mkheadsurf, 'output_img', apply_mask_2, 'mask_file')

wf.connect(apply_mask_2, 'out_file', outputnode, 'mp2rage')
wf.connect(mkheadsurf, 'output_img', outputnode, 'headmask')
wf.connect(mkheadsurf, 'output_surf', outputnode, 'headsurf')
