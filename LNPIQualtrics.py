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
            return None
        
    
        
    def getContactsMailingList(self,mailingListId,output='json'):
        
        """
        get the Contacts Mailing List
        
        for json output, to get the list of the contacts use:
        result['result']['elements']
        """
        directoryId = self.directoryId   # "POOL_3fAZGWRVfLKuxe3"

        baseUrl = "https://{0}.qualtrics.com/API/v3/directories/{1}/mailinglists/{2}/contacts"\
            .format(self.dataCenter, self.directoryId, mailingListId)
        headers = {
            "x-api-token": self.apiToken,
            }

        response = requests.get(baseUrl, headers=headers)
        # print(response.text)
            
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
            

def main(cmd='all', index=None, verbose=3):
    
    config = dotenv_values(".env")

    apiToken = config['APITOKEN']
    dataCenter = config['DATACENTER']
    directoryId = config['DIRECTORYID']
    
    qc = LNPIQualtrics(apiToken, dataCenter,directoryId)
    mailingLists = qc.getMailingLists()  
      
    if cmd == 'all':
        # get the list of mailingLists
        pp = pprint.PrettyPrinter(indent=4)
        for i in range(len(mailingLists)):
            print(f"==============")
            print(f"List index: {i+1}") 
            print(f"==============")
            pp.pprint(mailingLists[i])
    elif cmd == 'list':
        # retrieve contacts from the list specified by index
        # get the mailingListId fro the specified index
        mailingListId = mailingLists[index-1]['mailingListId']
        mailingList = qc.getContactsMailingList(mailingListId)
        updatedMailingList = qc.addContactLookupIdToList(mailingListId, mailingList)
        
        # print out the contents
        pp = pprint.PrettyPrinter(indent=4)
        for i in range(len(updatedMailingList)):
            print(f"==============")
            print(f"Subject index: {i+1}") 
            print(f"==============")
            pp.pprint(updatedMailingList[i])
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
                      default=0) 
    parser.add_argument("--verbose", type=int, help="verbose level default 3",
                         default=3)   
    args = parser.parse_args()
    

    test = False

    if test:
        print("Warning: running in test mode")
        args.index=1
        if args.index == 0:
            cmd = 'all'
        else:
            cmd = 'list'
        p = main(        
                    cmd = cmd,
                    index = args.index,
                    verbose=args.verbose
                )
    else:
        if args.index == 0:
            cmd = 'all'
        else:
            cmd = 'list'
        p = main(        
                    cmd = cmd,
                    index = args.index,
                    verbose=args.verbose
                )
        
      