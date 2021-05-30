#! /bin/bash -l

#SBATCH -J sierra-pywr
#SBATCH -o sierra-pywr.out
#SBATCH -e sierra-pywr.error
#SBATCH -n 1
#SBATCH -p fast.q
#SBATCH -t 00:15:00
#SBATCH --mail-user=lscaturchio@ucmerced.edu
#SBATCH --mail-type=begin,end,fail

module load anaconda3
echo 'Loaded anaconda module'
module load gcc-10.2.0
echo 'Loaded gcc module'
module load glpk/glpk-5.0 
echo 'Loaded glpk-5.0 module'

conda activate sierra-pywr
echo 'sierra-pywr environment initialized'

export SIERRA_DATA_PATH="/home/lscaturchio/data"
echo 'Exported SIERRA_DATA_PATH'
export SIERRA_RESULTS_PATH="@169.236.225.129:/VICElab/RESEARCH/PROJECTS/CERC-WET/Task7_San_Joaquin_Model/pywr_models/results"
echo 'Exported SIERRA_RESULTS_PATH'

cd sierra-pywr

python3 main.py -b merced -mp joblib

rsync ~/hi.txt -zaP lscaturchio@169.236.225.129:/VICElab/RESEARCH/PROJECTS/CERC-WET/Task7_San_Joaquin_Model/pywr_models/data
