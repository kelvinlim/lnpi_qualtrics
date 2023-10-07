# lnpi_qualtrics

Tools for automating qualtrics surveys.

## Prerequisites for running code

You will need to setup a virtual environment.  To do this you will need a python 3.10 installation.

```
# create the virtual environment
python3.10 -mvenv .venv
# activate the environment (mac and linux)
source .venv/bin/activate
# activate the environment (windows powershell)
.venv\Scripts\Activate.ps1

# install the packages using pip
pip install -r requirements.txt

```

## Command for querying mailing Lists

This tool is for querying the mailingLists associated with your account.  First complete the .env file which contains information on your account needed for querying. This can be located on the qualtrics site by selecting the circle in the top right corner and then Account Settings followed by QualtricsIDs tab. You will the API Token, the Datacenter ID and the Default Directory which will go into then entries APITOKEN, DATACENTER and DIRECTORYID respectively.

.env

example file for va

```
APITOKEN=FAKEIe58WHnDjwvB0zk0vabc13gas635dd
DATACENTER=gov1
DIRECTORYID=POOL_3fAZGWRVfLKuxe3
# For VA, set VERIFY=False
VERIFY=False
```

To get the list of your mailingLists, run the following command. Note the List index number before each entry. This will be used in the next step.

```
./LNPIQualtrics.py
```

To get detailed information about each subject in the mailing list (e.g., contactId, contactLookupId ) from a specific mailingList, use the index number as the argument.

```
./LNPIQualtrics.py --index 1
```

## Extract Response Data

First get the list of your surveys.

```
./LNPIQualtrics.py --cmd surveys
```

From the output, find the Survey index for the for the Survey you want to extract.

Now provide the index in the command.  This will extract all the data into a json file with the name of  the survey and a datetime stamp.  This will be placed in your current directory.

```
./LNPIQualtrics.py --cmd surveys --index 1
```

The decoders for tasks defined in the decoders directory are automatically applied to any values data matching the name found in modules in the decoders(e.g., SpatialSpan, TrailsAB).

To generate a csv output suitable for use as a dataframe, use the following options. The file will end in _df.csv

```
./LNPQualtrics.py --cmd surveys --index 1 --dataframe
```

To add the extRef from the mailingList, pass the name of the mailing list.

```
./LNPIQualtrics.py --cmd surveys --dataframe --extref 'cLBP Mailing List' --index 16
```
