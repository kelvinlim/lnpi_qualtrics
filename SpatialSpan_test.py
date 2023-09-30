import json
from decoders import *

def checkTrialType(ditem):
    
    return ditem['trial_type']
    pass

file = 'SampleData/sspan02.json'
with open(file) as fp:
    txt = fp.read()

dlist = json.loads(json.loads(txt))

result = SpatialSpan.decode(dlist)
# expect value to be 1.0
assert result['SpatialSpan3_perc_accuracy'] == 1.0, f"expected 1.0"
result2 = SpatialSpan.decode(-1)
assert result2['SpatialSpan3_perc_accuracy'] == None, f"expected None"

pass