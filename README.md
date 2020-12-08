# Route engine

# Prepare env
alias python=python3

sudo apt install -y python3-pip
pip3 install package_name

python -m pip install -U --user wheel six
python -m pip install -U --user ortools
python -m pip install -U --user requests

python -m pip uninstall ortools

# Running
python3 problem.py

# Refs
https://developers.google.com/optimization/routing/vrp
https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/doc/VRP.md#drop-nodes-constraints

# venv
pip list
pip install wheel six ortools requests
