# Usage

## wrapper

`meegpype-wrapper` runs the meegpype pipelines inside the Docker image (or with
Apptainer when `--apptainer` is given).

### forward


```{argparse}
:module: meegpype_wrapper.entrypoint
:func: get_parser
:prog: meegpype-wrapper
:path: forward
```