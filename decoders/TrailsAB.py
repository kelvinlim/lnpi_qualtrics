import os
import pandas as pd
import statistics
import json


# function that accepts the json data and returns the result in a dict


def decode(gridData,label='Grid'):
    
    # check that there is data
    if type(gridData) is list:
        # just get the trial_types we want
        grid_dict = [x for x in gridData if x['trial_type'] == 'trails']

        # get time_elapsed for each trailsType
        
        results = {}
        for item in grid_dict:
            key = f"{label}{item['trailsType']}_secs"
            value = item['time_elapsed']
            # convert to seconds float
            value = value/1000.0
            results[key]=value
            # add the inverse of secs so that higher values are better
            new_key = key + "inv"
            value=1.0/value
            results[new_key]=value
    else:
        # empty results
        results = {
            f"{label}A_secs": None,
            f"{label}B_secs": None,            
            f"{label}A_secsinv": None,
            f"{label}B_secsinv": None, 
        }
        
    return results    
        


