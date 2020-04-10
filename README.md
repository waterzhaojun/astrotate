# astrotate
Collection of lab experiment data organization and analysis. 
All experiments organized by different parts. info is stored in database. Raw data is stored locally. We may use different analysis method to treat same data. So the analysis result suppose to store in the raw data folder with analysis method name. The main analysis result should be a csv file because it is easier to load in Dash in the future. If need to create some figure or related files, save the output in the analysis result folder (figure and txt should based on this result).

============================================================================
## root folder
The root folder contains some common used functions and functions related to exp data input.

ep.py <br>
Electrophysiology experiment input module.

twop.py <br>
two photon experiment input module. After each day's experiment, you need to use twop.Exp2P to build a exp obj, then use this exp obj to build each twop.Runpara obj as it need treatement variable.

surgery.py <br>
Functions used to login the animal surgery information.

notebook.py <br>
Functions and class to manage nb table in database.


============================================================================
## transgenic
The files in this folder is used to manage the transgenic animal colony.


# ep
To extract animal list for specific ep experiment, you first need to run 'get_exp_animal_list', then by using different filter function to filt out the proper list.