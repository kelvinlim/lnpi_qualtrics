#! /usr/bin/env python

"""

LNPI code for working with qualtrics

Kelvin O. Lim
"""
import requests
import sys
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
import numpy as np
import textwrap

import yaml

pp = pprint.PrettyPrinter(indent=4)


__version_info__ = ('0', '2', '4')
__version__ = '.'.join(__version_info__)
version_history= \
"""
0.2.4 - make qualtrics_token default env file
0.2.3 - added use of config_qualtrics.yaml for configuration for full
        compatibility with other qualtrics scripts such as qualtrics_util
0.2.2 - changed default env file to be the qualtrics_token file to ease
        compatiblity with other qualtrics scripts such as qualtrics_util
0.2.1 - make dataframe output the default, expand help
0.2.0 - add -H argument
0.1.3 - add arg for sublist
0.1.2 - fixed bug in decode to check for multiple empty cog task entries None,'-1','{}'
0.1.1 - add label output using second row from the webfile
0.1.0 initial

To build:

pyinstaller --hidden-import decoders.SpatialSpan --hidden-import decoders.TrailsAB --onefile LNPIQualtrics.py

"""

class LNPIQualtrics:
    
    """
    Class for working with qualtrics
    
    """
    
    def __init__(self, apiToken, dataCenter,directoryId,
                 verify=True,nodecode=False,rawdata=False,
                 dataframe = False, extref=None,sublist=None):
        
        self.apiToken = apiToken
        self.dataCenter = dataCenter
        self.directoryId = directoryId
        self.verify = verify
        self.nodecode=nodecode
        self.rawdata=rawdata
        self.dataframe = dataframe
        self.extref = extref
        self.sublist = sublist

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
       
    def generateDescriptions(self,df)->str:
        """
        creates mapping of variable name to description
        
        from webfile, first row contains the variable name and the second row the description
        
        output in yaml dict format to make it easier to generate config file
        
        """
        # get the variables
        vars = list(df.columns)
        # get the first row
        firstRow = df.iloc[0]
        
        text  = "-\n"
        text += "  op: rename\n"
        text += "  arg:\n"

        for index in range(len(firstRow)):
            # remove \n from  description
            description = firstRow[index].replace('\n',' ')
            text += f"    {vars[index]}: {description}\n"
            pass
        return text
    
    def getResponsesWebFile(self, surveyId, webfile, format=format):
        
        """
        Get the responses from a downloaded web csv file
        
        """
        self.format = format
        
        # read in the file
        df = pd.read_csv(webfile)
        # generate descriptions
        descriptions = self.generateDescriptions(df)
        # drop first two rows
        newdf = df.drop([0,1])
        # convert newdf to a json string
        json_str = newdf.to_json(orient="records")
        # convert to list
        responses_list = json.loads(json_str)
            
        # create newFileName from webfile, replace .csv with json
        newFileName = webfile.replace('.csv','.json')   
        if self.rawdata:
            # write out the raw data to a json file
            with open(newFileName, "w") as fp:
                json.dump(responses_list, fp, indent=4)
            
        # process the Responses
        # ddict = self.processResponses(surveyId, {"responses":responses_list})
        
        new_responses = []
        # simulate the "values"
        for item in responses_list:
            tmp_dict = {}
            tmp_dict['values'] = item
            new_responses.append(tmp_dict)
            pass
        # place into another dict with key of "responses"
        ddict = {}
        ddict['responses'] = new_responses
        if self.nodecode == False:
            ddict = self.decodeData(ddict)
            pass

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
                        extRef = emailLookup.get(data['values']['RecipientEmail'], None)
                        # add to ddict['responses'][index]['values']['extRef']
                        if extRef is not None:
                            abc_dummy = 1
                            pass
                        ddict['responses'][index]['values']['extRef'] = extRef
                        pass
            if mailingListId == None:
                # error no match
                print(f"Error, no mailingList with name {self.extref} was found. Please recheck the name")
                sys.exit(1)
        elif self.sublist:
            # use csv file mapping email to id
            ml_df = pd.read_csv(self.sublist)
            # convert into a dict
            email_dict  = ml_df.set_index('emails').to_dict(orient='dict')['id']

            # do lookup of ddict['responses'][index]['recipientEmail']
            for index, data in enumerate(ddict['responses']):
                #extRef = emailLookup.get(data['values']['RecipientEmail'], None)
                extRef = email_dict.get(data['values']['RecipientEmail'], np.nan)

                # add to ddict['responses'][index]['values']['extRef']
                # check for nan
                if not np.isnan(extRef):
                    abc_dummy = 1
                    pass
                ddict['responses'][index]['values']['extRef'] = extRef

            pass
            
        # add the surveyInfo
        dt = datetime.now()
        surveyInfo = self.getSurveyInformation(surveyId)
        ddict['surveyInfo'] = surveyInfo
        ddict['extractionDateTime'] = str(dt)
            
        # create description file
        descFileName = webfile.replace('.csv','_descr.txt') 
        with open(descFileName, "w") as fp:
            fp.write(descriptions)
            
        if self.dataframe:
            # output the 'values' as a csv using a dataframe
            df = self.createDataFrame(ddict)
            # change the name of the file
            dfFileName = newFileName.replace(".json","_df.csv")
            df.to_csv(dfFileName, index=False)
        pass
       
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
            # data = self.exportResponsesFile(surveyId, fileId=fileId)
            responses_list, newFileName = self.getDownloadRest(surveyId, fileId = fileId)
            
            if self.rawdata:
                # write out the raw data to a json file
                with open(newFileName, "w") as fp:
                    json.dump(responses_list, fp, indent=4)
                
            # process the Responses
            ddict = self.processResponses(surveyId, responses_list)
            if self.dataframe:
                # output the 'values' as a csv using a dataframe
                df = self.createDataFrame(ddict)
                # change the name of the file
                dfFileName = newFileName.replace(".json","_df.csv")
                df.to_csv(dfFileName)
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
                        sys.exit(1)
                    
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

    def getDownloadRest(self, surveyId, fileId = None):
        """ 
        get the download through the REST API
        
        returns responses_list (dict) and the newFilename 
        """
        
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
                # self.nodecode = True  # don't decode data
                format = '.json'
                
            if format=='.json':
                # read json into a dict
                ddict = json.loads(fileContents) 

        else:
            print(f"Error: {response.status_code}")
            pp.pprint(response.content)
            return None    
                        
        return ddict, newFileName
    
    def processResponses(self, surveyId, ddict, format='json'):
        """
        Process the responses
        
        """
        surveyInfo = self.getSurveyInformation(surveyId)
        
        if format == 'json':        
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
                            # get subject email if it exists
                            subj_email = data['values'].get('recipientEmail',None)
                            extRef = emailLookup.get(subj_email, None) 
                            # add to ddict['responses'][index]['values']['extRef']
                            ddict['responses'][index]['values']['extRef'] = extRef
                            pass
                if mailingListId == None:
                    # error no match
                    print(f"Error, no mailingList with name {self.extref} was found. Please recheck the name")
                    sys.exit(1)
                
            # add the surveyInfo
            dt = datetime.now()
            ddict['surveyInfo'] = surveyInfo
            ddict['extractionDateTime'] = str(dt)
            
        return ddict

    def processResponses_orig(self, surveyId, ddict, format='json'):
        """
        Process the responses
        
        """
        surveyInfo = self.getSurveyInformation(surveyId)
        
        if format == 'json':        
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
                    sys.exit(1)
                
            # add the surveyInfo
            dt = datetime.now()
            ddict['surveyInfo'] = surveyInfo
            ddict['extractionDateTime'] = str(dt)
            
        return ddict

    
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
                # check if task data is here
                # values seen None and '-1', '{}
                # check if tdata is a str
                tdata = response['values'].get(task, None)
                if tdata in ['-1','{}']:
                #if tdata == '-1':
                    # set to None
                    tdata = None
                if type(tdata) == str:
                #if tdata is not None or (tdata != '-1'):
                #if task in response['values'].keys():
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
        nodecode = False, rawdata=False, extref=None,webfile=None,sublist=None,
        config_file = 'config_qualtrics.yaml'               
    ):
    
    environ = dotenv_values(env)

    apiToken = environ['QUALTRICS_APITOKEN']
    
    # read these from the yaml config file
    with open(config_file) as fp:
        config=yaml.safe_load(fp)
        
    dataCenter = config['account']['DATA_CENTER']
    directoryId = config['account']['DEFAULT_DIRECTORY']
    verify = config['account'].get('VERIFY',True)
    
    qc = LNPIQualtrics(apiToken, dataCenter,directoryId, verify=verify,
                       nodecode=nodecode, rawdata=rawdata, 
                       dataframe=True, extref = extref,sublist=sublist,
                    )
    
    mailingLists = qc.getMailingLists()  

    pp = pprint.PrettyPrinter(indent=4)
    
    if mailingLists == None:
        print(f"Error, no mailingLists found")
        sys.exit(1)

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
    elif cmd == 'surveys' and webfile != None:
        
        # retrieve surveys accessible by the user
        surveyLists = qc.getSurveyList()
        
        # get the surveyId for the index
        surveyId = surveyLists[index-1]['id']
        
        qc.getResponsesWebFile(surveyId, webfile, format=format)
        
    elif cmd == 'surveys' and index==None:
        # retrieve surveys accessible by the user
        surveyLists = qc.getSurveyList()
        
        # print out the contents
        #pp = pprint.PrettyPrinter(indent=4)
        for i in range(len(surveyLists)):
            print(f"Surveyindex: {i+1} Title: {surveyLists[i]['name']}") 


    elif cmd == 'surveyslong' and index==None:
        # retrieve surveys accessible by the user
        surveyLists = qc.getSurveyList()
        
        # print out the contents
        #pp = pprint.PrettyPrinter(indent=4)
        for i in range(len(surveyLists)):
            print(f"==============")
            print(f"Survey index: {i+1} Title: {surveyLists[i]['name']}") 
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
    
    description = textwrap.dedent('''\
    Gets information about MailingLists and Surveys. 
    
    Two files are used to configure the program. The first is a yaml file
    which defaults to config_qualtrics.yaml. This file contains the DATA_CENTER and 
    DEFAULT_DIRECTORY. The second file is a qualtrics_token file which contains the 
    QUALTRICS_APITOKEN. These are the same files that are used by qualtrics_util
    program.
 
    Here are some examples of using the command. Text following the $ is
    the command that is entered at the command line in a terminal window.
    
    $ LNPIQualtrics
    Without any arguments, the  surveys accessible by the user are listed with their index. 
    
    $ LNPIQualtrics  --index 1
    This will retrieve the responses for the survey with the index 1. Output is in a csv file. 
    Cognition data is decoded by default.

    $ LNPIQualtrics --index 1 --rawdata
    This will retrieve the raw data for the survey with the index 1. Output is in a json file.
  
    $ LNPIQualtrics --cmd list
    Without the --cmd list argument, the list of accessible mailingLists are listed with their index. 
   
    $ LNPIQualtrics --cmd list --index 1
    When the index argument is provided, then contact details for that mailingList are printed.
       
    $ LNPIQualtrics --cmd surveys --index 1 --rawdata
    This will retrieve the raw data for the survey with the index 1. Output is in a json file.
''')
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--config", type = str,
                     help="config file, default is config_qualtrics.yaml",
                     default='config_qualtrics.yaml'
                     ) 
    parser.add_argument("--sublist", type = str,
                     help="name of file for subject email to id mapping, default None",
                      default=None) 
    parser.add_argument("--env", type = str,
                     help="name of file containing api token in the current directory, default qualtrics_token",
                      default="qualtrics_token") 
    parser.add_argument("--index", type = int,
                     help="index number of mailingList to print",
                      default=None) 
    parser.add_argument("--verbose", type=int, help="verbose level default 3",
                         default=3)   
    parser.add_argument("--cmd", type=str, help="command to run, [all, list, surveys], default surveys",
                         default='surveys')  
    parser.add_argument("--format", type=str, help="output format, [json,csv], default json",
                         default='json')  
    #parser.add_argument('--test', dest='feature', default=False, action='store_true')
    parser.add_argument('--nodecode', help="do not decode taskdata", action='store_true')
    parser.add_argument('--rawdata', help="dump raw data", action='store_true')
    parser.add_argument('--webfile', type=str, help="read survey data from csv download through qualtrics web site", 
                        default=None)
    parser.add_argument('--extref', type=str, help="use extref from mailing list as id, matching with email- give the mailing list name",
                        default=None)
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('-H', '--history', help='Show version history', action='store_true')
    args = parser.parse_args()
    
    if args.history:
        print(f"{os.path.basename(__file__) } Version: {__version__}")
        print(version_history)
        sys.exit(0)



    p = main(        
                cmd = args.cmd,
                index = args.index,
                verbose=args.verbose,
                env=args.env,
                format = args.format, 
                nodecode = args.nodecode,
                rawdata = args.rawdata,
                extref = args.extref,  
                webfile = args.webfile,
                sublist = args.sublist,
                config_file=args.config

            )
        
      