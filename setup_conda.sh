#!/bin/bash

echo "Creating conda environment for cities-cif  scripts"
conda init
conda activate base
conda remove -n cities-cif  --all --yes
conda env create --file environment.yml --yes

echo "Switching back to cities-cif  Conda environment"
conda init
conda activate cities-cif 

