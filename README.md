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

## Command for querying mailingLists

This tool is for querying the mailingLists associated with your account.  First complete the .env file which contains information on your account needed for querying. This can be located on the qualtrics site by selecting the circle in the top right corner and then Account Settings followed by QualtricsIDs tab. You will the API Token, the Datacenter ID and the Default Directory which will go into then entries APITOKEN, DATACENTER and DIRECTORYID respectively.

.env

```
APITOKEN=FAKEIe58WHnDjwvB0zk0vabc13gas635dd
DATACENTER=ca1
DIRECTORYID=POOL_3fAZGWRVfLKuxe3
```

To get the list of your mailingLists, run the following command. Note the List index number before each entry. This will be used in the next step.

```
./LNPIQualtrics.py
```

To get detailed information about each subject in the mailing list (e.g., contactId, contactLookupId ) from a specific mailingList, use the index number as the argument.

```
./LNPIQualtrics.py --index 1
```
