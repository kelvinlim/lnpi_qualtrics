import os
import pandas as pd
import statistics
import json
import get_response


#near accuracy means they got the right location, but wrong order
def nearAccuracy(recalled,correct):
    acc=0
    for ii in recalled:
        if (ii in correct):
            acc+=1
    
    return(acc)
 
def spanRecall(spanJson):  
    #attempting to filter
    span_recall = [x for x in spanJson if x['trial_type'] == 'spatial-span-recall']

    for x in span_recall:
        print(x) 
        keys = x.keys()
        print(keys)
        values = x.values()
        print(values)
    
    ## based on using pandas
    span=pd.json_normalize(span_recall)

    #need to remove first two rows if they did the instructions (i.e., there are 8 rows)
    if len(span)>6:
        span.drop([0,1])

    meandistance=[]
    #take the mean distance for each set 
    for n in range(len(span.distance)):
        tmp=[i for i in span['distance'][n] if i is not None]
        meandistance.append(statistics.mean(tmp))
        
    span['meandistance']=meandistance

    nearAcc=[]
    #check near accuracy for each row
    for n in range(len(span.recall)):
        print(n)
        recall= [int(i) for i in span.recall[n]]
        nearAcc.append(nearAccuracy(recall, span.stimuli[n]))

    span['nearAcc']=nearAcc

    #could also add in whether or not they guessed more or less than the set number?
    #mean accuracy is calculated a percentage here
    #currently makes it into a table based on set size, but might be better to do as a single row?
    res = pd.DataFrame(columns = ['setsize','meanRT', 'meanAccuracy','meanDistance','meanNearAccuracy'])
    for n in [3,4,5]:
        res=res.append({'setsize': n, 'meanRT': statistics.mean(span.rt.loc[span['set_size'] == n]),\
            'meanAccuracy': statistics.mean(span.accuracy.loc[span['set_size'] == n])/n,\
            'meanDistance': statistics.mean(span.meandistance.loc[span['set_size'] == n]),\
            'meanNearAccuracy': statistics.mean(span.nearAcc.loc[span['set_size'] == n])/n},\
                ignore_index = True)
    return(res)


def gridPerformance(gridJson):
    grid_dict = [x for x in gridJson if x['trial_type'] == 'trails']

    for x in gridJson: 
        keys = x.keys()
        print(keys)
        values = x.values()
        print(values)


    grid=pd.json_normalize(grid_dict)
    #currently makes table with each trail (A and B) as row. Do we want a single row?

    meandist=[]
    #take the mean distance for each set 
    for n in range(len(grid.missDistance)):
        tmp=[i for i in grid['missDistance'][n] if i is not None]
        meandist.append(statistics.mean(tmp))
        
    grid['meandistance']=meandist


    res= pd.DataFrame(columns = ['trailsType','RT', 'numErrors','meanDistance'])

    for n in ["A","B"]:

        res=res.append({'trailsType': n, 'RT': statistics.mean(grid.rt.loc[grid['trailsType'] == n]),\
            'numErrors': len(grid.missBoxValue.loc[grid['trailsType'] == n]),\
            'meanDistance': statistics.mean(grid.meandistance.loc[grid['trailsType'] == n])},\
                ignore_index = True)
    return(res)


#need to pull in the survey info from participants
#get_survey_info.main() #can I implement this?
#get_response #<-how do I implement this?

#need to generalize
#could identify a particular subject or loop through all participants
#with open("sampledata2.json") as jsonFile:
#    data=json.load(jsonFile)
#need to make a variable data that is a single participant's regular survey result
jsonDataSpan = data['values']['SpatialSpan']
jsonDataGrid = data['values']['TrailsAB']

##span##
spanJson = json.loads(jsonDataSpan)
#print(json.dumps(spanJson,sort_keys=True, indent=4))

SpanResults=spanRecall(spanJson)

##grid##
gridJson = json.loads(jsonDataGrid)
