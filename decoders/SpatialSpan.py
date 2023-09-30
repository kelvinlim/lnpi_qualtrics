# function that accepts the json data and returns the result in a dict

from statistics import mean

# for spatial scan
def decode(jsonData, label='SpatialSpan'):
    
    # expecting set_sizes of 3,4,5
    # create a dictionary of lists to hold accuracy of each
    
    accuracy = {
        "3": [],
        "4": [],
        "5": []
    }
    
    results={}
    if type(jsonData) is list:
        for item in jsonData:
            if item['trial_type'] == 'spatial-span-recall':
                # append accuracy to the proper bin
                accuracy[str(item['set_size'])].append(item['accuracy'])
                #print(item)
        # calculate different metrics
        # percent correct
        for key in accuracy.keys():
            # calculate mean and then percent correct
            meanAccuracy = mean(accuracy[key])
            percentCorrect = meanAccuracy/float(key)
            # store in  results
            newKey = f"{label}{key}_perc_accuracy"
            results[newKey]=percentCorrect      
            pass
    else:
            for key in ["3","4","5"]:
                newKey = f"{label}{key}_perc_accuracy"
                results[newKey]=None
    return results
