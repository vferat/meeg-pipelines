# Installation

## wrapper

meegpype is shipped as a containerized application. The easiest way to install it is to use the meegpype-wrapper library, which will handle the installation of the container and its dependencies. To use the wrapper, you need to have Python 3.8 or higher installed on your system as well as either Docker or Apptainer (also known as Singularity) installed. 

To install the wrapper, you can use pip:

```bash
pip install -U git+https://github.com/vferat/meeg-pipelines.git#subdirectory=wrapper
```