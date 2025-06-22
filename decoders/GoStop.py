# function that accepts the json data and returns the result in a dict

from statistics import mean

from .impulsivity_process import ImpulsivityProcess

# for GoStop
def decode(jsonData, label='GoStop'):

    # instantiate the object
    obj = ImpulsivityProcess()
    
    results = obj.gostop_score(jsonData)

    return results
