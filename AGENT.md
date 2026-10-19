# AGENT.md

## Project Structure

### doc
The ``/doc`` folder contains the documentation of the project. The documentation is generated using sphinx and can be built using the ``make html`` command.
It contains also the documentation for the wrapper library.

### meegpype

meegpype is a python package that contains the code to run the pipelines.

#### Interfaces

The ``/meegpype/interfaces`` folder contains nipype interfaces need for the pipelines.

#### Workflows

The ``/meegpype/workflows`` folder  contains nipype workflows that achieve a specific goal and that can be reused to create pipelines.


#### Pipeline

the ``/meegpype/pipelines`` folder contains the full pipeleins that can be run by the users


#### dokcer

the ``/docker`` folder contains fiels to generate a docker image that is can be used to run the computations.

### wrapper

The ``/wrapper`` folder contain a python library that warps the ``/meegpype/pipelines`` into docker run commands.
Users can  install a contianer enginge docker and the wrapepr library to simply run the pipelines.
The wrapper is meant to handle both docker and apptainer containers. 

### Docker

The ``/docker`` folder contains files to build a docker image that contains all the dependencies to run the pipelines.

### Dependencies
The project provides a docker image that contains all the dependencies to run the pipelines.
The docker image is based on `smriprep`. Since the default smriprep image does not contain all freesurfer tools, the docker image is built from a fork of the smriprep.
The image is available at ghcr.io/vferat/smriprep:0.19.1 and is build manually from the forked smriprep repository.

### Building the docker image

