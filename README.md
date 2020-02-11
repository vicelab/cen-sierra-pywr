# sierra-pywr

Code base for modeling the central Sierra Nevada hydropower systems and implementing said models to optimize performance and 
make predictions of future scenarios

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Get your environment set up, depending on your Operating System, as well as IDE, install 
[Pywr](https://pywr.github.io/pywr-docs/master/index.html)

```sh
$ sudo apt-get install libgmp3-dev libglpk-dev glpk
```


## Installation

A step by step series of examples that tell you how to get a development env running

#### Linux:

1. If you choose to use Anaconda environment for OS X or Linux and remove the installation file:

```sh
$ wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
$ rm Anaconda3-2019.03-Linux-x86_64.sh
```
2. Check the version of Conda you have installed
```sh
conda --version
conda update conda
```

2. Create and activate new environment

```sh
conda create --name *environment_name*
conda activate *environment_name*
```

3. Add channels and install packages

```sh
conda config --add channels conda-forge
conda config --add channels pywr
conda install pywr
```
4. Once on the repository, install the requirements
```sh
$ pip install -r requirements.txt
```

#### Windows:

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

## Running the Models 

```
conda activate *environment_name*
```

### Flags

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

## Setting up models in Merced Cluster

We are going to be looking at the Merced Cluster implementing the user Manual. For more information, check the [Merced Cluster User Manual](http://hpcwiki.ucmerced.edu/knowledgebase/merced-cluster-user-manual/)

1. Request an account [here](http://hpcwiki.ucmerced.edu/knowledgebase/getting-a-merced-account) for access to the cluster
2. Access the UC Merced VPN via Cisco Anyconnect, 

[Windows Setting up](https://ucmerced.service-now.com/kb_view.do?sysparm_article=KB0010636) \
[Windows Connecting](https://ucmerced.service-now.com/kb_view.do?sysparm_article=KB0010500) \
[Linux Setting up](https://ucmerced.service-now.com/kb_view.do?sysparm_article=KB0010634) \
[Linux Connecting](https://ucmerced.service-now.com/kb_view.do?sysparm_article=KB0010499)

3. Using a linux terminal:
```sh

$ ssh <username>@merced.ucmerced.edu   
```
4. Once logged in, check to see what content is available.

```sh

$ ls
help data scratch
```
In order to execute jobs, the cluster uses a workload manager called [Slurm](https://slurm.schedmd.com/)

5. Run a test job in the cluster using one of the files under the help section, in this case: projectile.exe

```sh

$ vim projectile.exe
```
Looking at the #SBATCH scripts, the following is what is standard usage for running tasks in the cluster. Any more, and there could be issues such as potentially getting your account revoked.

```sh
 #SBATCH --nodes=1
 #SBATCH --ntasks=1
 #SBATCH --cpus-per-task=1
 #SBATCH --mem-per-cpu=1G
 #
 #SBATCH --partition fast.q 
 #SBATCH --time=0-00:15:00     # 0days 15 minutes
 #
 #SBATCH --output=myjob_%j.stdout
 #
 #SBATCH --job-name=test
 #SBATCH --export=ALL
```
6. After analyzing the code, you can run it via these commands on the termninal:

```sh

$ cp ~/help/projectile.exe ~/
$ cp ~/help/sample.sub ~/
```

7. Setup Modules for your environment:

* module avail - lists all modules
* module_load <mod_name> - loads the environment based on <mod_name>
* module list - provides a list of all modules currently loaded into the user environment. 
* module unload <mod_name> - unloads the environment corresponding to <mod_name>.
* module swap <mod_1> <mod_2> - unloads the environment corresponding to <mod_1> and loads that corresponding to <mod_2>.

## Built With

* [Pywr](https://pywr.github.io/pywr-docs/master/index.html) - The main library used
* [Python Flask](https://maven.apache.org/) - Dependency Management

## Authors

* **David Rheinheimer** - [rheinheimer](https://github.com/rheinheimer)
* **Aditya Sood** - [asood12](https://github.com/asood12)
* **Dan Tran** - [GateauXD](https://github.com/GateauXD)
* **Lorenzo Scaturchio** - [gr8monk3ys](https://github.com/gr8monk3ys)

See also the list of [contributors](https://github.com/vicelab/sierra-pywr/contributors) who participated in this project.
