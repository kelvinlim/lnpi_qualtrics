# lnpi_qualtrics

Tools for automating tasks for managing data from qualtrics surveys.


To build executable:
```
pyinstaller --hidden-import decoders.SpatialSpan --hidden-import decoders.TrailsAB --hidden-import yaml --onefile LNPIQualtrics.py

```
## Prerequisites for running code

You will need to setup a virtual environment.  To do this you will need at least a python 3.10 installation.

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

This tool is for querying the mailingLists associated with your account.  First complete the .env file which contains information on your account needed for querying. This can be located on the qualtrics site by selecting the circle in the top right corner and then Account Settings followed by QualtricsIDs tab. You will need the API Token, the Datacenter ID and the Default Directory which will go into then entries APITOKEN, DATACENTER and DIRECTORYID respectively.



example qualtrics_token file for va

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
./LNPIQualtrics.py --cmd surveys --extref 'cLBP Mailing List' --index 22
```

## Use a web csv file downloaded through the qualtrics web GUI

This is the preferred download method since it provides more information than the API approach. 

```
# Use the provided ExternalReference column from the data export file from qualtrics for the subject ID.
# 
./LNPIQualtrics.py --cmd surveys --index 1 --webfile ../cda_r34happiness/R34+EMA+spinal+cord+injury_June+13,+2025_22.48.csv

This generates two files based on the webfile:
1. xxx_df.csv - survey data and decoded task data
2. xxx_desc.txt - a txt file with the run_parse commands to rename the variables based on the information in the webfile

Here is an example of the desc.txt output. Notice that it provides
part of the survey question:

-
  op: rename
  arg:
    StartDate: Start Date
    EndDate: End Date
    Status: Response Type
    IPAddress: IP Address
    Progress: Progress
    Duration (in seconds): Duration (in seconds)
    Finished: Finished
    RecordedDate: Recorded Date
    ResponseId: Response ID
    RecipientLastName: Recipient Last Name
    RecipientFirstName: Recipient First Name
    RecipientEmail: Recipient Email
    ExternalReference: External Data Reference
    LocationLatitude: Location Latitude
    LocationLongitude: Location Longitude
    DistributionChannel: Distribution Channel
    UserLanguage: User Language
    Q_RecaptchaScore: Q_RecaptchaScore
    QN01_intensity_NP: Right now, what is your neuropathic pain intensity?
    QN02_control_NP: Right now, how in control do you feel about your neuropathic pain?
    QN03_concerned_NP: Right now, how concerned are you about your neuropathic pain?
    QN04_affect_funct_NP: Right now, how much is your neuropathic pain affecting your daily functioning?
    QN05_fearful_move_NP: Right now, how fearful are you about moving because of your neuropathic pain?
    QN06_activity: What activity did you do since your last diary entry?
    QN07_low_exerc_min: How many minutes did you exercise/were you active?
    QN08_mod_exerc_min: How many minutes did you exercise/were you active?
    QN09_high_exerc_min: How many minutes did you exercise/were you active?
    QN10_sleep_hours: How many hours of sleep did you get?
    QN11_sleep_falling: Did you have trouble falling asleep?
    QN12_sleep_staying: Did you have trouble staying asleep?
    QN13_sleep_waking: Did you have trouble with waking up too early?
    Q01_panas_active: Active
    Q02_panas_determined: Determined
    Q03_panas_attentive: Attentive
    Q04_panas_inspired: Inspired
    Q05_panas_alert: Alert
    Q06_panas_afraid: Afraid
    Q07_panas_nervous: Nervous
    Q08_panas_upset: Upset
    Q09_panas_hostile: Hostile
    Q10_panas_ashamed: Ashamed
    Q01_control_life: Right now, how in control do you feel about your life in general?
    Q02_body_energy: Right now, how ENERGETIC does your body feel?
    Q03_body_relax: Right now, how RELAXED does your BODY feel?
    Q04_mind_relax: Right now, how RELAXED does your MIND feel?
    Q41_Fitbit: A quick reminder to leave your Fitbit app open on your phone so we can collect the data.
    TrailsAB-int: Did anything interrupt you during the previous task?
    SymmetrySpan-int: Did anything interrupt the previous task?
    SpatialSpan: SpatialSpan
    TrailsAB: TrailsAB


```



```
# using the mailing list to provide the External Data Reference (id of subject)
./LNPIQualtrics.py --cmd surveys  --extref 'cLBP Mailing List' --index 2 --webfile ../cda_emapain/proj_backpain/EMA+chronic+low+back+pain_December+7,+2023_13.13.csv

# for covidema
./LNPIQualtrics.py --cmd surveys   --extref "Test covid ema" --webfile ../cda_covidema/proj_covid240709/Long+COVID+EMA+survey_July+9,+2024_22.24.csv --index 12 

```

## Using web download of Responses instead of using REST API.

For scipain ema study, certain variables (QN07-13) were not present when retrieved using REST API but were present when downloaded using the Web interface.

We need an option to use the web download csv file instead of using the REST version.

Currently use self.exportResponseFile() which also does the decode,
relabeling and replace user info with extRef

## Implement new  steps

Have four methods to separate processes

1) read_web_csv - Read the web download file and returns data a resources_list which is a list of dictionaries.
2) getDownloadRest - get the responses data from the rest api as list of dictionaries.
3) processResponses(responses_list) - do processing of responses, input is the responses_list, returns a new responses_list
4) saveResponsesFile(responses_list, fileinfo)

## To make the executable

```
pyinstaller --onefile LNPIQualtrics.py

Error on execution  LNPIQaultrics -V

Traceback (most recent call last):
  File "LNPIQualtrics.py", line 21, in <module>
    from decoders import *
AttributeError: module 'decoders' has no attribute 'SpatialSpan'
[49974] Failed to execute script 'LNPIQualtrics' due to unhandled exception!

## suggestions from CoPilot

Check Hidden Imports: Ensure that all necessary modules are included in the PyInstaller build. You can use the --hidden-import flag to specify any missing modules. For example:


pyinstaller --hidden-import decoders.SpatialSpan --hidden-import decoders.TrailsAB --onefile LNPIQualtrics.py

Debug Imports: Build your app with the --debug=imports flag to get a detailed list of imports and see if any are missing:

pyinstaller --debug=imports LNPIQualtrics.py


```
