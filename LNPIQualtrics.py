#! /usr/bin/env python

"""

LNPI code for working with qualtrics

Kelvin O. Lim
"""
import requests
import json
# Setting user Parameters
from dotenv import dotenv_values
import argparse
import pprint
import pandas as pd
import time
import zipfile
import io
import os
from datetime import datetime
from decoders import *

pp = pprint.PrettyPrinter(indent=4)

class LNPIQualtrics:
    
    """
    Class for working with qualtrics
    
    """
    
    def __init__(self, apiToken, dataCenter,directoryId,
                 verify=True,nodecode=False,rawdata=False,
                 dataframe = False, extref=None):
        
        self.apiToken = apiToken
        self.dataCenter = dataCenter
        self.directoryId = directoryId
        self.verify = verify
        self.nodecode=nodecode
        self.rawdata=rawdata
        self.dataframe = dataframe
        self.extref = extref

    def getMailingLists(self):
        """
        get a list of MailingList

        /API/v3/directories/{directoryId}/mailinglists
 
        """
        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists?includeCount=true"\
            .format(self.dataCenter, self.directoryId)
        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers, verify=self.verify)
        
        # if OK
        if response.status_code == 200:
            # retrieve the CGC
            # convert to dict
            ddict = json.loads(response.text)
            mailingLists = ddict['result']['elements']
            return mailingLists
        else:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return None

    def getSurveyInformation(self, surveyId):
        """
        get the survey design, provides important information about the questions and 
        design of the survey which aid in its interpretation.

        see: https://api.qualtrics.com/67b9315910902-managing-surveys
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}".format(dataCenter, surveyId)
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/surveys".format(dataCenter)
        
        format - output format, default json, others are df for dataframe
        """
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}".format(self.dataCenter, surveyId)
        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers,verify=self.verify)
        
        # if OK
        if response.status_code == 200:
            # retrieve the CGC
            # convert to dict
            ddict = json.loads(response.text)
            surveyInfo = ddict['result']
            return surveyInfo
        else:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return None    
                
    def getSurveyList(self, format='json'):
        """
        get a list of Surveys accessible for this user

        see:  https://api.qualtrics.com/67b9315910902-managing-surveys#list-surveys
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/surveys".format(dataCenter)
        
        format - output format, default json, others are df for dataframe
        """
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/surveys".format(self.dataCenter)
        baseUrl = f"https://{self.dataCenter}.qualtrics.com/API/v3/surveys"

        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers, verify=self.verify)
        
        # if OK
        if response.status_code == 200:
            # retrieve the CGC
            # convert to dict
            ddict = json.loads(response.text)
            lists = ddict['result']['elements']
            # convert to a df
            df = pd.DataFrame(lists)
 
            self.surveyLists = lists
            if format == 'json':
                output = lists
            elif format =='df':
                output = df
            return output
        else:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return None       
            
    def getContactLookupId(self, mailingListId, contactId):
        """
        gets the ContactLookupId for a specific contactId in a mailingListId
        
        The ContactLookupId begins with "CGC_" and is a required parameter when
        sending out a distribution from  a mailing list to an  individual.
        
        
        API/v3/directories/{directoryId}/mailinglists/{mailingListId}/contacts/{contactId}
 
        """
        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists/{2}/contacts/{3}"\
            .format(self.dataCenter, self.directoryId, mailingListId, contactId)
        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers, verify=self.verify)
        
        # if OK
        if response.status_code == 200:
            # retrieve the CGC
            # convert to dict
            ddict = json.loads(response.text)
            contactLookupId = ddict['result']['contactLookupId']
            return contactLookupId
        else:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return None        
    
        
    def getContactsMailingList(self,mailingListId,output='json'):
        

        directoryId = self.directoryId   # "POOL_3fAZGWRVfLKuxe3"

        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists/{2}/contacts"\
            .format(self.dataCenter, self.directoryId, mailingListId)
        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers, verify=self.verify)
        # print(response.text)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return ModuleNotFoundError

        if output == 'raw':
            return response
        elif output == 'json':
            # convert json into a dict
            rawdict = json.loads(response.text)
            return rawdict['result']['elements']
        
    def addContactLookupIdToList(self,mailingListId, mailingList):
        """
        Add contactLookupId to each entry in mailing list
        """
        
        for index in range(len(mailingList)):
            # get the contactId for this entry
            contactId = mailingList[index]['contactId']
            # get the contactLookupId
            contactLookupId = self.getContactLookupId(mailingListId, contactId)
            # add this to dictionary for this index
            mailingList[index]['contactLookupId'] = contactLookupId
            pass
        return mailingList
       
       
    def getResponses(self, surveyId, format='json'):
        """
        get the responses
        """
        
        self.format = format
        
        # start response request
        progressId = self.exportResponsesStart(surveyId, format=self.format)
        # poll the request
        fileId = self.exportResponsesProgress(surveyId, progressId)
        if fileId != None:
            # get the file
            data = self.exportResponsesFile(surveyId, fileId=fileId)
            pass
        

        
    """
    get responses
    1. request the responses
        iad1.qualtrics.com/API/v3/surveys/SV_bwrylOA5nNnI9M1/export-responses
        https://api.qualtrics.com/6b00592b9c013-start-response-export
        
        https://yul1.qualtrics.com/API/v3/surveys/{surveyId}/export-responses
        
        body  {
            "format": "json"  # or csv
            "timeZone": "America/Chicago"
            } 
            
            
        {
            "result": {
                "progressId": "ES_0d2n60qVHB9jSLz",
                "percentComplete": 0.0,
                "status": "inProgress"
            },
            "meta": {
                "requestId": "7a9150e0-08bb-4953-89cf-ef8a157b8aa7",
                "httpStatus": "200 - OK"
            }
        }     
    """
    def exportResponsesStart(self, surveyId, format='json'):
        
        baseUrl = f"https://{self.dataCenter}.qualtrics.com/API/v3/surveys/{surveyId}/export-responses"
        headers = {
            "x-api-token": self.apiToken,
        }
        
        data = {
            "format": format
        }
        response = requests.request("POST", baseUrl, json=data, headers=headers,verify=self.verify)
        
        # if OK
        if response.status_code == 200:
            # convert to dict
            ddict = json.loads(response.text)
            # get the progressId for next step
            self.progressId = ddict['result']['progressId']
            return self.progressId
        else:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return None
        
    """
    2. Poll for progress on the export using the Get Response Export Progress
        'iad1.qualtrics.com/API/v3/surveys/SV_bwrylOA5nNnI9M1/export-responses/ES_0d2n60qVHB9jSLz'
        https://api.qualtrics.com/37e6a66f74ab4-get-response-export-progress
        
        https://yul1.qualtrics.com/API/v3/surveys/{surveyId}/export-responses/{exportProgressId}
    
        Need the fileId
        {
            "result": {
                "fileId": "1dc4c492-fbb6-4713-a7ba-bae9b988a965-def",
                "percentComplete": 100.0,
                "status": "complete"
            },
            "meta": {
                "requestId": "a5a2db6c-3fab-4363-92dc-debddcc51e40",
                "httpStatus": "200 - OK"
            }
        }
    """    
    def exportResponsesProgress(self, surveyId, progressId=None):
        """
        Poll export process until completed and have a fileId
        """
        
        # set fileId to None
        fileId = None
        
        if progressId == None:
            # set
            progressId = self.progressId
        
        baseUrl = f"https://{self.dataCenter}.qualtrics.com/API/v3/surveys/{surveyId}/export-responses/{progressId}"
        
        headers = {
            "x-api-token": self.apiToken,
        }
        
        count = 0
        # wait for 20 sec or fileId
        while fileId == None and count < 20:
            response = requests.get(baseUrl, headers=headers, verify=self.verify)
        
            # if OK
            if response.status_code == 200:
                # convert to dict
                ddict = json.loads(response.text)
                # check if there is fileId, means that export is completed
                if "fileId" in ddict['result'].keys():
                    fileId = ddict['result']['fileId']
            
            time.sleep(2)
            count += 2   # increment the counter
            
        if fileId != None:
            self.fileId = fileId
            return self.fileId
        else:
            print(f"Error: No fileId after {count} seconds")
            pp.pprint(response.content)
            return None
            
    """    
    3. When progress is complete, get the file  Get Response Export File
        https://api.qualtrics.com/41296b6f2e828-get-response-export-file
        
        https://yul1.qualtrics.com/API/v3/surveys/{surveyId}/export-responses/{fileId}/file
        
    """
    
    def exportResponsesFile(self, surveyId, fileId=None):
        """ 
        export the file
        """
            
            
        surveyInfo = self.getSurveyInformation(surveyId)
        
        if fileId == None:
            fileId = self.fileId
            
        baseUrl = f"https://{self.dataCenter}.qualtrics.com/API/v3/surveys/{surveyId}/export-responses/{fileId}/file"
        
        headers = {
            "x-api-token": self.apiToken,
        }
        response = requests.get(baseUrl, headers=headers, verify=self.verify)
        # if OK
        if response.status_code == 200:
            # file is in response.content
            zf = zipfile.ZipFile(io.BytesIO(response.content))
            # assume only one file
            origFileName = zf.filelist[0].filename
            
            # get the filetype from the file suffix
            format = os.path.splitext(origFileName)[1]  # returns .json or .csv
            # create a datetime string for the filename
            dt = datetime.now()
            str_date_time = dt.strftime("%Y%m%d_%H%M")
            
            # replace the spaces with _
            newFileName = origFileName.replace(" ","_")
            # replace {format} with datetime{format}
            newFileName = newFileName.replace(f"{format}", f"_{str_date_time}{format}")

            # extract the file
            # open the file and read the contents 
            with zf.open(origFileName) as myFile:
                fileContents = myFile.read()
            
            if self.rawdata:
                self.nodecode = True  # don't decode data
                format = '.json'
                
            if format=='.json':
                # read json into a dict
                ddict = json.loads(fileContents)
                if self.nodecode == False:
                    ddict = self.decodeData(ddict)
                    ddict = self.relabelData(ddict, surveyInfo)
                    # convert a list with single item to a number
                    ddict = self.delistValues(ddict)
                    
                if self.extref:
                    # get the mailing list and add the extref variable,
                    # matching based on the email from mailing list and the survey
                    mailingLists = self.getMailingLists()
                    
                    mailingListId = None
                    for mailingListEntry in mailingLists:
                        # match the name with extref
                        if mailingListEntry['name'] == self.extref:
                            mailingListId = mailingListEntry['mailingListId']
                            # get the mailingList
                            mailingList = self.getContactsMailingList(mailingListId)
                            # create lookup dictionary  email, extref
                            emailLookup = {}
                            for item in mailingList:
                                emailLookup[item['email']] = item['extRef']
                                pass
                            
                            # do lookup of ddict['responses'][index]['recipientEmail']
                            for index, data in enumerate(ddict['responses']):
                                extRef = emailLookup.get(data['values']['recipientEmail'], None)
                                # add to ddict['responses'][index]['values']['extRef']
                                ddict['responses'][index]['values']['extRef'] = extRef
                                pass
                    if mailingListId == None:
                        # error no match
                        print(f"Error, no mailingList with name {self.extref} was found. Please recheck the name")
                        exit(1)
                    
                # add the surveyInfo
                ddict['surveyInfo'] = surveyInfo
                ddict['extractionDateTime'] = str(dt)
                
                if self.dataframe:
                    # output the 'values' as a csv using a dataframe
                    df = self.createDataFrame(ddict)
                    # change the name of the file
                    dfFileName = newFileName.replace(".json","_df.csv")
                    df.to_csv(dfFileName)
                    
                # output json with indents
                with open(newFileName, mode='w') as newFile:
                    json.dump(ddict, newFile, indent=4)
                pass
                #zipfile.ZipFile(io.BytesIO(response.content)).extractall('.')
            elif format=='.csv':
                with open(newFileName, mode='wb') as newfile:
                    newfile.write(fileContents)
        else:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return None     

    def createDataFrame(self, ddict):
        """
        Create a dataframe from the values in each response
        
        """    
        rows = []  # hold list of dict
        for response in ddict['responses']:
            rows.append(response['values'])
                        
        df = pd.DataFrame.from_dict(rows)             
        return df
    
    def relabelData(self, ddict, surveyInfo):
        """
        Relabel the data using the questionName from surveyInfo
        
        surveyInfo['questions']['QID40']['questionName']

        Args:
            ddict (list of dicts): survey data from qualtrics 
        """
        newdict = {"responses": []}
        
        for response in ddict['responses']:
            # make a copy of original since we are changing the keys!
            origResponseValuesKeys = list(response['values'].keys())
            for dataKey in origResponseValuesKeys:

                # for debugging scipain data                    
                # if dataKey in ['QID73','QID76','QID77']:
                #     xyz = 1
                #     pass
                
                if dataKey in surveyInfo['questions'].keys():
                    # get the newLabel
                    newLabel = surveyInfo['questions'][dataKey]['questionName']
                    # relabel
                    response['values'][newLabel] = response['values'].pop(dataKey)
                pass
        
            newdict['responses'].append(response)
             
        return newdict
    
    def delistValues(self, ddict):
        """
        converts list to a single numeric value
        
          "QN06_activity": [
                    "5"
                ],

        Args:
            ddict (list of dicts): survey data from qualtrics 
        """
        newdict = {"responses": []}
        
        for response in ddict['responses']:

            for key in response['values'].keys():
                # check if value is a list
                if type(response['values'][key]) is list:
                    if len(response['values'][key]) == 1:
                        # convert the first element of the list to a number
                        response['values'][key] = float(response['values'][key][0])
                        pass
                    else:
                        response['values'][key] = None
                        
            newdict['responses'].append(response)
             
        return newdict
        
    def decodeData(self, ddict, remove=True):
        """
        Decode task data using modules in decoders
        
        ddict  - the dictionary containing the json data from the task
        remove - flag to remove the original column from the response
        """
        
        def get_module_names(package_name='decoders'):
            import pkgutil
            package = __import__(package_name)
            module_names = [name for _, name, _ in pkgutil.walk_packages(package.__path__)]

            for module_name in module_names:
                #print(module_name)
                pass
            return module_names
        
        tasks = get_module_names()
        
        newdict = {"responses": []}
        
        for response in ddict['responses']:
            
            for task in tasks:
                # check if task is here
                if task in response['values'].keys():
                    # get the json string and convert into a dict
                    taskData = json.loads(response['values'][task]) 
                    
                    # call the method for this data
                    result = eval(f"{task}.decode(taskData)")
                    # append result
                    response['values'].update(result)

                    # remove original data
                    if remove:
                        response['values'].pop(task)                    
            newdict['responses'].append(response)
            pass
        
        return newdict

def main(cmd='all', index=None, verbose=3,env='.env', format='json',
        nodecode = False, rawdata=False, dataframe = False, extref=None               
):
    
    config = dotenv_values(env)

    apiToken = config['APITOKEN']
    dataCenter = config['DATACENTER']
    directoryId = config['DIRECTORYID']
    if "VERIFY" in config.keys():
        if config['VERIFY'] == 'True':
            verify=True
        elif config['VERIFY'] == 'False':
            verify = False
    else:
        verify = True
    
    qc = LNPIQualtrics(apiToken, dataCenter,directoryId, verify=verify,
                       nodecode=nodecode, rawdata=rawdata, 
                       dataframe=dataframe, extref = extref)
    
    mailingLists = qc.getMailingLists()  

    pp = pprint.PrettyPrinter(indent=4)
    
    if mailingLists == None:
        print(f"Error, no mailingLists found")
        exit(1)

    if cmd == 'list' and index==None:
        # get the list of mailingLists
        for i in range(len(mailingLists)):
            print(f"==============")
            print(f"List index: {i+1}  {mailingLists[i]['name']}") 
            print(f"==============")
            pp.pprint(mailingLists[i])
    elif cmd == 'list':
        # retrieve contacts from the list specified by index
        # get the mailingListId fro the specified index
        mailingListId = mailingLists[index-1]['mailingListId']
        mailingList = qc.getContactsMailingList(mailingListId)
        updatedMailingList = qc.addContactLookupIdToList(mailingListId, mailingList)
        
        # print out the contents
        #pp = pprint.PrettyPrinter(indent=4)
        for i in range(len(updatedMailingList)):
            print(f"==============")
            print(f"Subject index: {i+1} {mailingLists[index-1]['name']} {updatedMailingList[i]['email']}") 
            print(f"==============")
            pp.pprint(updatedMailingList[i])
    elif cmd == 'surveys' and index==None:
        # retrieve surveys accessible by the user
        surveyLists = qc.getSurveyList()
        
        # print out the contents
        #pp = pprint.PrettyPrinter(indent=4)
        for i in range(len(surveyLists)):
            print(f"==============")
            print(f"Survey index: {i+1} {surveyLists[i]['name']}") 
            print(f"==============")
            pp.pprint(surveyLists[i])
    elif cmd == 'surveys':
        # retrieve surveys accessible by the user
        surveyLists = qc.getSurveyList()
        
        # get the surveyId for the index
        surveyId = surveyLists[index-1]['id']

        # get the responses
        qc.getResponses(surveyId, format=format)

    pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Get information about MailingLists and Surveys. Account information is
        read from a .env file which contains the APITOKEN, DATACENTER and DIRECTORYID.
        Without any arguments, the mailingLists are listed with the index. 
        When the index argumennt is provided, then contact details for that mailingList are printed.
        
        To extract the survey data, first use the --cmd surveys to get the index for the survey you 
        want to extract.  Then add the --index number  argument where number is the index of your
        survey that you want to extract.
        """
    )
 
    parser.add_argument("--env", type = str,
                     help="name of env file in the current directory, default .env",
                      default=".env") 
    parser.add_argument("--index", type = int,
                     help="index number of mailingList to print",
                      default=None) 
    parser.add_argument("--verbose", type=int, help="verbose level default 3",
                         default=3)   
    parser.add_argument("--cmd", type=str, help="command to run, [all, list, surveys], default list",
                         default='list')  
    parser.add_argument("--format", type=str, help="output format, [json,csv], default json",
                         default='json')  
    #parser.add_argument('--test', dest='feature', default=False, action='store_true')
    parser.add_argument('--nodecode', help="do not decode taskdata", action='store_true')
    parser.add_argument('--rawdata', help="dump raw data", action='store_true')
    parser.add_argument('--dataframe', help="create csv dataframe", action='store_true')
    parser.add_argument('--extref', type=str, help="use extref from mailing list as id, matching with email- give the mailing list name",
                        default=None)

    args = parser.parse_args()
    

    test = False

    if test:
        print("Warning: running in test mode")

        cmd = args.cmd
        cmd = 'surveys'
        index = 16
        mailingListName = 'cLBP Mailing List'
        p = main(        
                    cmd = cmd,
                    index = index,
                    verbose=args.verbose,
                    env=args.env,
                    format = 'json', #args.format, 
                    nodecode = args.nodecode,
                    rawdata = args.rawdata,
                    dataframe = True, #args.dataframe,  
                    extref = mailingListName, #   args.extref,              
                )
    else:

        p = main(        
                    cmd = args.cmd,
                    index = args.index,
                    verbose=args.verbose,
                    env=args.env,
                    format = args.format, 
                    nodecode = args.nodecode,
                    rawdata = args.rawdata,
                    dataframe = args.dataframe,                
                    extref = args.extref,              

                )
        
      