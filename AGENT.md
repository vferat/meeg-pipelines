

## Project Structure

### Interfaces

The ``/meegpype/interfaces`` folder contains nipype interfaces need for the pipelines.

### Workflows

The ``/meegpype/workflows`` folder  contains nipype workflows that achieve a specific goal and that can be reused to create pipelines.


### Pipeline

the ``/meegpype/pipelines`` folder contains the full pipeleins that can be run by the users


### dokcer

the ``/docker`` folder contains fiels to generate a docker image that is can be used to run the computations.

### wrapper

The ``/meegpype/wrapper`` folder contain a python library that warps the ``/meegpype/pipelines`` into docker run commands.
Users can only install docker and the wrapepr library to simply run the pipelines.
