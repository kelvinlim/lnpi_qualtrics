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

pp = pprint.PrettyPrinter(indent=4)

class LNPIQualtrics:
    
    """
    Class for working with qualtrics
    
    """
    
    def __init__(self, apiToken, dataCenter,directoryId):
        
        self.apiToken = apiToken
        self.dataCenter = dataCenter
        self.directoryId = directoryId
        
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

        response = requests.get(baseUrl, headers=headers)
        
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
        
    def getSurveyList(self, format='json'):
        """
        get a list of Surveys accessible for this user

        see:  https://api.qualtrics.com/67b9315910902-managing-surveys#list-surveys
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/surveys".format(dataCenter)
        
        format - output format, default json, others are df for dataframe
        """
        
        baseUrl = "https://{0}.qualtrics.com/API/v3/surveys".format(self.dataCenter)

        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers)
        
        # if OK
        if response.status_code == 200:
            # retrieve the CGC
            # convert to dict
            ddict = json.loads(response.text)
            lists = ddict['result']['elements']
            # convert to a df
            df = pd.DataFrame(lists)
 
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

        response = requests.get(baseUrl, headers=headers)
        
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

        response = requests.get(baseUrl, headers=headers)
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
            

def main(cmd='all', index=None, verbose=3,env='.env'):
    
    config = dotenv_values(env)

    apiToken = config['APITOKEN']
    dataCenter = config['DATACENTER']
    directoryId = config['DIRECTORYID']
    
    qc = LNPIQualtrics(apiToken, dataCenter,directoryId)
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
            print(f"Subject index: {i+1} {mailingLists[i]['name']} {updatedMailingList[i]['email']}") 
            print(f"==============")
            pp.pprint(updatedMailingList[i])
    elif cmd == 'surveys':
        # retrieve surveys accessible by the user
        surveyLists = qc.getSurveyList()
        
        # print out the contents
        #pp = pprint.PrettyPrinter(indent=4)
        for i in range(len(surveyLists)):
            print(f"==============")
            print(f"Study index: {i+1} {surveyLists[i]['name']}") 
            print(f"==============")
            pp.pprint(surveyLists[i])
    pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Get information about MailingLists. Account information is
        read from a .env file which contains the APITOKEN, DATACENTER and DIRECTORYID.
        Without any arguments, the mailingLists are listed with the index. When the index argumennt
        is provided, then contact details for that mailingList are printed."""
    )
 
    parser.add_argument("--index", type = int,
                     help="index number of mailingList to print",
                      default=None) 
    parser.add_argument("--verbose", type=int, help="verbose level default 3",
                         default=3)   
    parser.add_argument("--env", type=str, help="name of env file, default .env",
                         default='.env')  
    parser.add_argument("--cmd", type=str, help="command to run, [all, list, surveys], default all",
                         default='all')  
    args = parser.parse_args()
    

    test = False

    if test:
        print("Warning: running in test mode")
        args.index=1
        if args.index == 0:
            cmd = 'all'
        else:
            cmd = 'list'
        cmd = 'surveys'
        p = main(        
                    cmd = cmd,
                    index = args.index,
                    verbose=args.verbose,
                    env=args.env
                )
    else:

        p = main(        
                    cmd = args.cmd,
                    index = args.index,
                    verbose=args.verbose,
                    env=args.env
                )
        
      