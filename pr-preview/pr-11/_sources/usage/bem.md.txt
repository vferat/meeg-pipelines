# bem

The `bem` workflow allows to compute the BEM surfaces for a given subject. It is a wrapper around the {func}`~meegpype.pipelines.bem.run_bem_pipeline` function. It expects that the subject's MRI data is already preprocessed using the `freesurfer` `recon-all` pipeline.
The `bem` workflow can be run using the default `watershed` method (see {func}`~meegpype.workflows.anat.bem.generate_basic_bem_workflow` for details) or the experimental ``refined`` method (see {func}`~meegpype.workflows.anat.bem.generate_refined_bem_workflow` for details).
 
```{argparse}
:module: meegpype_wrapper.entrypoint
:func: get_parser
:prog: meegpype-wrapper
:path: bem
```
