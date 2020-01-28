# sierra-pywr

Code base for modeling the central Sierra Nevada hydropower systems and implementing said models to optimize performance and 
make predictions of future scenarios

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes 
through our very own application called Dash.

### Prerequisites

Get your environment set up, depending on your Operating System, as well as IDE, we advise installing 
[Pywr](https://pywr.github.io/pywr-docs/master/index.html)


### Installing

A step by step series of examples that tell you how to get a development env running

OS X & Linux:

```sh
sudo apt-get install libgmp3-dev libglpk-dev glpk
sudo apt-get install liblpsolve55-dev lp-solve
```

Windows:

1. Install Anaconda Environment
2. Create new environment
3. Install the necessary packages (Pywr)
4. Import your environment into your IDE

```
conda activate *environment_name*
-b *network* -n "development" -d d

or

-b *network* -p -n "development" -d dm
```

## Built With

* [Pywr](https://pywr.github.io/pywr-docs/master/index.html) - The main library used
* [Python Flask](https://maven.apache.org/) - Dependency Management

## Authors

* **David Rheinheimer** - [rheinheimer](https://github.com/rheinheimer)
* **Aditya Sood** - [asood12](https://github.com/asood12)
* **Lorenzo Scaturchio** - [gr8monk3ys](https://gr8monk3ys)

See also the list of [contributors](https://github.com/vicelab/sierra-pywr/contributors) who participated in this project.

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
