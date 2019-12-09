# astrotate
Collection of lab experiment data organization and analysis

============================================================================
## root folder
The root folder contains some common used functions and functions related to exp data input.

ep.py <br>
Electrophysiology experiment input module.

twop.py <br>
two photon experiment input module. After each day's experiment, you need to use twop.Exp2P to build a exp obj, then use this exp obj to build each twop.Runpara obj as it need treatement variable.

surgery.py <br>
Functions used to login the animal surgery information.


============================================================================
## transgenic
The files in this folder is used to manage the manage the transgenic animal colony

