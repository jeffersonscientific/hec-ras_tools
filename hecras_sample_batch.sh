#!/bin/bash
#
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8g
#SBATCH --time=24:00:00
#SBATCH --output=hecras_%j.out
#SBATCH --error=hecras_%j.err
#SBATCH --partition=serc
#
# A sample batch script to run hecras Linux, specifically on Stanord's Sherlock HPC. This script also uses modules that may be specific to a
#  Stanford Earth environment.
# Basically:
# 1) load modules
# 2) set ulimit -s unlimited , in case codes try to run large arrays on the stack. This needs to be evaluated. Might not be necessary.
# 3) Set runtime parameters. Source data (geometry, plan files) should be in the _INPUT directory. The python scrip will create WORKING_DIR
#  and copy files if necessary.
# 4) run the python script.
#
module use /oak/stanford/schools/ees/share/cees/modules/modulefiles
module purge
module load anaconda/3
module load hec-ras
#
# the python script will do this, but it's probably a good habit... or maybe we actually don't need to do this. don't know yet.
ulimit -s unlimited
#
# set run variables:
PROJECT_NAME="SMC_010"
GEOM_INDEX=5
PLAN_INDEX=1
#
# allow for inputs. for now, just positional:
if [[ ! -z $1 ]]; then PROJECT_NAME=$1; fi
if [[ ! -z $2 ]]; then GEOM_INDEX=$2; fi
if [[ ! -z $3 ]]; then PLAN_INDEX=$3; fi
#
# set the location of the hecras source and workin_ dir. the script will create the working_dir if necessary.
#INPUT_DIR="/scratch/users/${USER}/hecras/PescaderoButano_original"
INPUT_DIR="/oak/stanford/schools/ees/jsuckale/hhampson/PescaderoButano"
WORKING_DIR="/scratch/users/${USER}/hecras/work_dir_`printf %02d ${GEOM_INDEX}`_`printf %02d ${PLAN_INDEX}`"
#
# add an OUTPUT_DIR. Copy completed job data here
OUTPUT_DIR="${GROUP_HOME}/${USER}/hecras_outputs/work_dir_`printf %02d ${GEOM_INDEX}`_`printf %02d ${PLAN_INDEX}`$"
DO_COPY=0

python ${HECRAS_TOOLS_DIR}/hecraspy.py ${PROJECT_NAME} ${GEOM_INDEX} ${PLAN_INDEX} input_dir=${INPUT_DIR} working_dir=${WORKING_DIR} do_execute=1
#
if [[ ${DO_COPY}=1 ]]; then
    if [[ ! -d ${OUTPUT_DIR} ]]; then
        mkdir -p ${OUTPUT_DIR}
    fi
    cp -r ${WORKING_DIR} ${OUTPUT_DIR}
fi

