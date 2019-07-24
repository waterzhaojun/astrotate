1. edit treatment.json
2. edit project.json
3. edit templates/animal_cno.json
3. if you have singleneuron data, edit templates/data_singleneuron.csv. And when you run exp.py, don't forget to set type with s.

use exp.py to init a folder for that day's exp

set -e with exp date. The format is like 190520

if the data type contains b, you have to set --bchannel (if the channel name is not '1 BF') and --freq (better output the txt file as 1 hz)

fill treatment.json. Right now the trials and points doesn't work. You have to change the treatment points in each data type manually after upload.

fill animal_cno.json (for other type animal json file). 

for single neuron, fill singleneuron.json. but right now it doesn't be used. This part need to be added in next round.
also for single neuron data, fill in data_singleneuronMec.csv according to the template format.

