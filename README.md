# sierra-pywr

Code base for modeling the central Sierra Nevada hydropower systems and implementing said models to optimize performance and 
make predictions of future scenarios

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

## Installation

A step by step series of examples that tell you how to get a development env running

### Linux:

Get your environment set up, depending on your Operating System, as well as IDE, install 
[Pywr](https://pywr.github.io/pywr-docs/master/index.html)

```sh
$ sudo apt-get install libgmp3-dev libglpk-dev glpk
```

1. If you choose to use Anaconda environment for OS X or Linux and remove the installation file:

```sh
$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ bash Miniconda3-latest-Linux-x86_64.sh

$ source ~/.bashrc
$ rm Miniconda3-latest-Linux-x86_64.sh
```
2. Check the version of Conda you have installed
```sh
$ conda --version
$ conda update conda
```

2. Create and activate new environment

```sh
$ conda create --name *environment_name*
$ conda activate *environment_name*
```

3. Add channels and install packages

```sh
$ conda config --add channels conda-forge
$ conda config --add channels pywr
$ conda install pywr
```
4. Once on the repository, install the requirements
```sh
$ pip install -r requirements.txt
```

### Windows

You can use either Anaconda or Python PIP. As follows:

#### Anaconda 

1. Install Anaconda Environment [here](https://www.anaconda.com/distribution/#download-section) and check what version

```cmd
conda --version
conda update conda
```

2. Create and activate new environment

```cmd
conda create --name *environment_name*
conda activate *environment_name*
```

3. Add channels and install packages

```cmd
conda config --add channels conda-forge
conda config --add channels pywr
conda install pywr
```

#### Python PIP

0. Install GLPK and add it to your environment path. 

Download v4.65 from: http://ftp.gnu.org/gnu/glpk/

Note that GLPK is in tarzip (.tar.gz) format, so you can use 7-zip to extract.

Save the resulting glpk-4.65 folder in a good place. Copy the full path to glpk-4.65\w64 to your environment path.
E.g.: add `C:\glpk-4.65\w64` to your global (or local) path.

0. Download/clone this repository

We recommend using PyCharm or Visual Studio Code for integrated VCS and IDE.

0. Download & install Python!
Version 3.7, 64-bit should work.

0. Create and activate a Python environment

Note that `env` is in .gitignore, so you can save the environment as "env" in sierra-pywr.

0. Install Python packages

From within the Python environment, install all requirements from `requirements.txt`.
e.g.: `pip install -r requirements.txt` 

## Running the Models

Running the models involves several steps, depending on the type of run.

All model runs will require three general steps.

1. Copy/sync data folder to the local computer.

2. Specify the data folder as an environment variable `SIERRA_PYWR_DATA`

3. Run the model from the command line.

As a simple example, the following will run the baseline Merced model:

`python main.py -b merced`

### Data preparation
For data preparation, see 

### Scenario setup

### Running

```
conda activate *environment_name*
```

*Flags*

* "-b", "--basin"
* "-nk", "--network_key"
* "-d", "--debug"
* "-p", "--include_planning"
* "-n", "--run_name"
* "-mp", "--multiprocessing"

For only daily models (Merced & Tuolomne):

```
python main.py -b *network* -n "development" -d d
```
For both daily and monthly models

``` 
python main.py -b *network* -p -n "development" -d dm
```

### Postprocessing

## Built With

* [Pywr](https://pywr.github.io/pywr-docs/master/index.html) - The main library used
* [Python Flask](https://maven.apache.org/) - Dependency Management

## Authors

* **David Rheinheimer** - [rheinheimer](https://github.com/rheinheimer)
* **Aditya Sood** - [asood12](https://github.com/asood12)
* **Dan Tran** - [GateauXD](https://github.com/GateauXD)
* **Lorenzo Scaturchio** - [gr8monk3ys](https://github.com/gr8monk3ys)

See also the list of [contributors](https://github.com/vicelab/sierra-pywr/contributors) who participated in this project.
