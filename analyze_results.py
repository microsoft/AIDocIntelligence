import os
import sys
import pandas as pd
import glob
import pathlib as Path
import json

def analyze():
    # pass in a directory
    fsarg = os.fsencode(sys.argv[1])
    if ( not os.path.isdir(fsarg)):
        print ('bad directory')
        return

    # create a dataframe over all json files in this directory
    dfs = [] # an empty list to store the data frames
    print (f'found {len(os.listdir(fsarg))} files in {sys.argv[1]}')

    for file in glob.glob(sys.argv[1] + '/*.json'):
        if (os.path.getsize(file) == 0):
            continue
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.json_normalize(data["candidate_process"])
        print(df)
        dfs.append(df) # append the data frame to the list
    
    temp = pd.concat(dfs, ignore_index=True) # concatenate all the data frames in the list.
    temp.to_csv(f'{sys.argv[1]}{os.sep}results.csv', sep=',', mode='w')


analyze()

# run this at command line with python -m analyze_results C:\temp\ipg-inv\processed\[batch stamp] (path to json output files)