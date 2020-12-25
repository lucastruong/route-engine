# Route engine

# venv
python3 --version
pip list
pip install wheel six ortools 
pip install polyline requests numpy

# Running
python3 problem.py

# Tools
Python Online: https://www.programiz.com/python-programming/online-compiler/
Calculator: https://www.calculatorsoup.com/calculators/math/speed-distance-time-calculator.php
HHMMSS: https://www.tools4noobs.com/online_tools/seconds_to_hh_mm_ss/
Polyline Decode: https://developers.google.com/maps/documentation/utilities/polylineutility
Distance: https://www.geodatasource.com/distance-calculator

# Deploy on Ubuntu
sudo apt update
sudo apt-get -y upgrade
sudo apt-get install -y python3-pip

python3 -V
pip3 -V
pip3 install polyline requests numpy
pip3 list

vi ~/.bashrc
alias python=python3
source ~/.bashrc

# Refs
https://developers.google.com/optimization/routing/vrp
https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/doc/VRP.md#drop-nodes-constraints
https://stackoverflow.com/questions/63112611/vehicle-routing-with-different-vehicle-speed-google-or-tools
https://stackoverflow.com/questions/62756122/how-to-limit-number-of-locations-for-each-vehicle-in-google-or-tools-route-optim
