import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='import single neuron data from template to exp folder')
parser.add_argument('-e', '--exp', type=str, required=True,
                    help='exp date, will use this as folder name. The format should be 190520')
parser.add_argument('-t', '--template', type=str, required=False,
                    help='the type of data. b represent blood flow. s represent single neuron. l represent lfp. m represent multi unit. o represent oxygen')
args = parser.parse_args()

