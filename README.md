# CenSierraPywr models

This repository includes the code base for modeling the hydropower systems of the primary tributaries of California's San Joaquin river.

This readme includes
* Project setup (software requirements, input data, environment variables, etc.)
* Installation (software and Python packages)
* How to run a model

## Project setup

This model uses Python and [Pywr](https://github.com/pywr/pywr), a Python package for modeling water systems using linear programming. Pywr depends on either GLPK or LPSolve to solve the LP problem. In this model, GLPK is assumed; LPSolve might work, but has not been tested.

### Software requirements

General software requirements are as follows:
1. [GLPK](https://www.gnu.org/software/glpk/) (version 4.65). The location of the 64-bit GLPK executable must be callable as `glpsol`.
2. Python 3.8.x, 64-bit. For Windows, this can be found at https://www.python.org/downloads/windows/.
3. All Python package requirements found in `requirements.txt` in the root folder.

See installation notes below for more detailed installation guidance.

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

**Windows notes**: Installing the required Pywr version (Pywr) may require compilation via a C++ compiler. On Windows this can be with [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/)

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

## Preparation of data

## Running a model

A model is typically run from the command line, calling `main.py` along with relevant arguments. The full list of arguments can be found in `main.py` or by calling `python main.py --help`.

Two basic arguments are particularly important: `-b [basin]` specifies which basin to run, while `-p` specifies whether to include the planning model. 

Here are some examples to work from:

* `python main.py -b stanislaus`: Run the Stanislaus model *without* planning for hydropower optimization
* `python main.py -b stanislaus -p`: Run the Stanislaus model *with* planning for hydropower optimization
* `python main.py -b stanislaus -p -d`: Run the Stanislaus model with planning, in debug mode.
* `python main.py -b stanislaus -p -d -m 8 -s 1985 -e 1996`: Run the Stanislaus model with planning, in debug mode, with 8 planning months starting in 1985 and ending in 1996, inclusive.

## Postprocessing

# Reproducibility

The following steps present a specific implementation of the code in this repository to facilitate reproducibility of the peer-reviewed publication of this work (in review). The objectives of this section are to reproduce the main results figures in the publication, with electricity price data and inflow hydrology as model input. Reference figures (e.g., the area map and electricity price boxplots) are not described. The general steps are as follows, described in detail below:

1. Install relevant software
2. Set-up environment variables
3. Install & preprocess input data
4. Run the models
5. Generate figures

It is assumed that this is performed on a PC with a 64-bit version of Windows 10+. For non-Windows computers, see the notes above for general guidance. Some of these steps may be skipped or modified as needed based on the experience of the modeler.

IMPORTANT: This is only for reproducing the single manuscript noted above. It is insufficient, for example, for using the model with other included basins, even though other basin data must be included in the preprocessing described.

## 1. Install relevant software

### C++ compiler
* If you don't already have Visual Studio installed, try [Visual Studio 2022](https://visualstudio.microsoft.com/vs/community/), making sure to select the "Desktop development with C++" installation option. 
 
### GLPK
* Download GLPK from https://ftp.gnu.org/gnu/glpk/glpk-4.65.tar.gz and extract to `C:\glpk-4.65`
* Add `C:\glpk-4.65\w64` to your `PATH` environment variable.
  
### Python 3.8
* Download Python 3.8.10, 64-bit from https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe and install.
* Create and activate a new Python environment using Python 3.8 (It is assumed that the modeler is able to create and work with Python environments; see above for more info). 
 
### CenSierraPywr (this repository)
* Download version `v2022.06.20` of this repository from: https://github.com/vicelab/cen-sierra-pywr/releases/tag/v2022.06.20, and extract to a location of your choice.
* From within the activated Python environment, install required Python packages found in `requirements.txt` using pip: `pip install -r requirements.txt` (The proficient Python modeler may choose their own preferred method to work with environments and install packages)

## 2. Set-up data structure and environment variables

* Data structure: Add an output directory. For example, `C:\data`.
* Create a new environment variable called `SIERRA_DATA_PATH` with the above directory. 

## 3. Install & preprocess input data

Some preprocessing is required.

Activate the project Python environment and navigate to `cen-sierra-pywr/preprocessing` in the Windows terminal before running any of the following preprocessing scripts.

### Electricity prices
* Note that this code repository already includes the original price dataset needed, though it still needs to be processed for use in the model, as follows.
* Run `python preprocess_electricity_prices.py -y 2009` (Note the year, which is important for reproducibility).

### Inflow hydrology
* Download the **April 25, 2022** version of the [bias-corrected runoff dataset](https://datadryad.org/stash/dataset/doi:10.6071/M3609B) and extract to the main data folder as follows: `[SIERRA_DATA_PATH]\original\hydrology\historical\Livneh\runoff\[all extracted files]` (e.g., to `C:\data\original\...`)
* Run `python preprocess_hydrology.py -d historical`

## 4. Run the models

All models are run from the root project folder (i.e., from `cen-sierra-pywr`), within the same Python environment as preprocessing. Run commands for each scenario are as follows:

* Stanislaus w/ planning, debug mode
  * `python main.py -b stanislaus -p -d -n "stanislaus - planning method"`
  * Note: "debug mode" outputs more detailed information, including all future planning months when planning is enabled.
* Stanislaus w/ planning, w/ ramp rate
  * `python main.py -b stanislaus -p -n "stanislaus - rr"`
* Stanislaus w/ planning, w/o ramp rate
  * This scenario requires a manual, one-time change to the model. In the file `./sierra/base_parameters/FlowRangeParameter.py`, on line 48, directly under `get_up_ramp_ifr` (i.e., one level in from `def`), add `rate = 1e6`. This will set the ramping rate to one million, effectively turning off the restriction. **IMPORTANT: Don't forget to undo this change!**
  * `python main.py -b stanislaus -p -n "stanislaus - no rr"`
* Upper San Joaquin w/o planning
  * `python main.py -b upper_san_joaquin -n "usj - no planning"`
* Upper San Joaquin w/ planning
  * `python main.py -b upper_san_joaquin -p -n "usj - planning"`

## 5. Generate figures

Figures can be generated by running each of three Python scripts, found in `./analyses/manuscript figures`. From within that folder, run each desired script to produce the corresponding figures.

# Authors

See the list of [contributors](https://github.com/vicelab/cen-sierra-pywr/contributors).
