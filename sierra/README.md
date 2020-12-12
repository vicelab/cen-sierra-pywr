# Central Sierra Nevada Pywr models

This repository includes the code base for modeling the hydropower systems of the primary tributaries of California's San Joaquin river.

This readme includes
* Project setup (software requirements, input data, environment variables, etc.)
* Installation (software and Python packages)
* How to run a model

## Project setup

This model uses Python and [Pywr](https://github.com/pywr/pywr), a Python package for modeling water systems using linear programming. Pywr depends on either GLPK or LPSolve to solve the LP problem. In this model, GLPK is assumed; LPSolve might work, but has not been tested.

### Software requirements

General software requirements are as follows:
1. [GLPK](https://www.gnu.org/software/glpk/) (version 4.65). The location of the 64-bit GLPK executable must be callable as `glpsol`; how this is done varies by operating system.
2. Python 3.8 (highest; Pywr does not work with version 3.9), 64-bit.
3. All Python package requirements found in `requirements.txt` in the root folder

### Input data
Input data is not stored within this repository, though the preprocessing scripts needed to create the input data are. The location of the input data is defined as an environment variable.

### Environment variables

Generally, two environment variables are needed, though other modifications to the system environment variables may be needed depending on the installation setup. These include:
1. `SIERRA_DATA_PATH` - This specifies the location of the input data (see below for notes on input data)
2. `SIERRA_RESULTS_PATH` - This specifies where to save results (csv files). This is optional. By default, results will be stored in a folder called `results` parallel to `SIERRA_DATA_PATH` or, if run in debug mode, in a project folder called `results`.

## Installation notes

Installation notes are provided for Windows and Linux (Debian-flavor). Installation on MacOS should be similar.

### Python environment setup

#### Virtual environment

It is highly recommended to work within a Python "virtual environment". A Python virtual environment is a copy of an installed Python version. It is beyond the scope of this readme to explain exactly what this means and how to use it, though there are many resources on the Internet about this, such as: [Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer/). 

Exactly how a virtual environment is set up depends on the package management system used, i.e. pip or Conda. If pip is used, the built-in Python virtual environment setup can be used. Alternatively, the `virtualenvwrapper` Python package can be used. If Conda is used, then conda would be used to create/start the virtual environment. A good Integrated Development Environment (see "Development environment" below) will help to create a virtual environment and/or switch to a specific virtual environment.

Although setting up virtual environments can be overwhelming/confusing at first, especially compared with, say, R, they are quite necessary due to the dynamic and rapidly evolving nature of Python and Python packages over time.

#### Development environment

Like programming languages generally, there are multiple ways to set up Python code on a computer to run. This model can be modified using a simple text editor and run only from the command line. Or, it can be run in a full featured integrated development environment (IDE), such as [PyCharm](https://www.jetbrains.com/pycharm/) or [Visual Studio Code](https://code.visualstudio.com/) (both of which are solid options, including the community edition of PyCharm, and are available for Mac, Windows and Linux).

**IDEs and virtual environments** A good IDE can also help with installing a virtual environment, whether the virtual environment is created with Conda or otherwise. How to do so is left to the reader as an exercise.

### GLPK

#### Windows

To install GLPK on Windows:
1. Download and extract GLPK to a folder of your choice (e.g., `C:\glpk-4.65`)
2. Add the 64-bit version to the `path` environment variable (e.g., `C:\glpk-4.65\w64`)

#### Linux

To install GLPK on Linux, use:

```sh
$ sudo apt-get install libgmp3-dev libglpk-dev glpk
```

### Python packages

Generally, pip or Conda are used to install/manage Python packages.

#### pip

Once in the project's virtual environment, install the Python packages as follows:

```sh
$ pip install -r requirements.txt
```

**Linux notes**: Pywr must be installed from source on Linux. Generally, the steps are:
1. Download the Pywr source code (make sure to download the version found in `requirements.txt`!).
2. From within the Pywr source code directory, install with `python setup.py install --with-glpk`

After this the rest of the requirements can be installed with pip as above.

#### Anaconda

1. Install Pywr

**NOTE**: These instructions will install version 1.8; modify this as needed to match what is in `requirements.txt`. 

```sh
$ conda config --add channels conda-forge
$ conda config --add channels pywr
$ conda install pywr==1.8
```

2. Once in the repository (and in the activated Conda virtual environment), install the requirements using pip as above.

## How to set up and run a model

[TO-BE-COMPLETED]

Running the models involves several steps, depending on the type of run.

All model runs will require three general steps.

1. Copy/sync data folder to the local computer.

2. Specify the data folder as an environment variable `SIERRA_PYWR_DATA`

3. Run the model from the command line.

As a simple example, the following will run the baseline Merced model:

`python main.py -b merced`


```
python main.py -b *network* -n "development" -d d
```
For both daily and monthly models

``` 
python main.py -b *network* -p -n "development" -d dm
```

## Authors

See the list of [contributors](https://github.com/vicelab/sierra-pywr/contributors).
