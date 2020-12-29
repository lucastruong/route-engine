# Route engine

# For Developer
brew install python
python3 -V
pip list
pip install wheel six ortools
pip install polyline requests numpy
pip install Flask

# Running
export FLASK_ENV=development
export FLASK_APP=app.py
python -m flask run -h 0.0.0.0  -p 5000

# Deploy on Ubuntu
sudo apt update
sudo apt install software-properties-common 
sudo add-apt-repository ppa:deadsnakes/ppa 
sudo apt update 
sudo apt install python3.9 
python3.9 -V

sudo apt-get install python3.9-distutils
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py

mkdir routeEngine && cd routeEngine
python3.9 -m venv venv

python3.9 -m pip install wheel six ortools
python3.9 -m pip install polyline requests numpy
python3.9 -m pip list

# Tools
Python Online: https://www.programiz.com/python-programming/online-compiler/
Calculator: https://www.calculatorsoup.com/calculators/math/speed-distance-time-calculator.php
HHMMSS: https://www.tools4noobs.com/online_tools/seconds_to_hh_mm_ss/
Polyline Decode: https://developers.google.com/maps/documentation/utilities/polylineutility
Distance: https://www.geodatasource.com/distance-calculator

# Refs
https://developers.google.com/optimization/routing/vrp
https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/doc/VRP.md#drop-nodes-constraints
https://stackoverflow.com/questions/63112611/vehicle-routing-with-different-vehicle-speed-google-or-tools
https://stackoverflow.com/questions/62756122/how-to-limit-number-of-locations-for-each-vehicle-in-google-or-tools-route-optim
