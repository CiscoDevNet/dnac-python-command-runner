"""
This script provides a function to get DNA-C authentication token
and functions to make DNA-C REST APIs request
All required modules are imported in this script so from other scripts just need to import this script
"""
import requests   # We use Python external "requests" module to do HTTP query
import json
import sys
from requests.auth import HTTPBasicAuth

#All DNA-C configuration is in dnac_config.py
import dnac_config  # DNA-C IP is assigned in dnac_config.py
from tabulate import tabulate # Pretty-print tabular data in Python

# It's used to get rid of certificate warning messages when using Python 3.
# For more information please refer to: https://urllib3.readthedocs.org/en/latest/security.html
requests.packages.urllib3.disable_warnings() # Disable warning message

def get_X_auth_token(ip=dnac_config.DNAC_IP,ver=dnac_config.VERSION,uname=dnac_config.USERNAME,pword=dnac_config.PASSWORD):
    """
    This function returns a new service ticket.
    Passing ip, ver,uname and pword when use as standalone function
    to overwrite the configuration above.

    Parameters
    ----------
    ip (str): dnac routable DNS addess or ip
    ver (str): dnac VERSION
    uname (str): user name to authenticate with
    pword (str): PASSWORD to authenticate with

    Return:
    ----------
    str: DNAC authentication token
    """

    # JSON input for the post ticket API request
    r_json = {
    "username": uname,
    "password": pword
    }
    # url for the post ticket API request
    post_url = "https://"+ip+"/api/system/"+ver+"/auth/token"
    # All DNAC REST API query and response content type is JSON
    headers = {'content-type': 'application/json'}
    # POST request and response
    try:
        r = requests.post(post_url, auth=HTTPBasicAuth(username=uname, password=pword), headers=headers,verify=False)
        # remove '#' if need to print out response
        #print (r.json()["Token"])

        # return service ticket

        return r.json()["Token"]
    except:
        # Something wrong, cannot get service ticket
        print ("Status: %s"%r.status_code)
        print ("Response: %s"%r.text)
        sys.exit ()

def get(ip=dnac_config.DNAC_IP,ver=dnac_config.VERSION,uname=dnac_config.USERNAME,pword=dnac_config.PASSWORD,api='',params=''):
    """
    To simplify requests.get with default configuration.Return is the same as requests.get

    Parameters
    ----------
    ip (str): dnac routable DNS addess or ip
    ver (str): dnac VERSION
    uname (str): user name to authenticate with
    pword (str): PASSWORD to authenticate with
    api (str): dnac api without prefix
    params (str): optional parameter for GET request

    Return:
    -------
    object: an instance of the Response object(of requests module)
    """
    ticket = get_X_auth_token(ip,ver,uname,pword)
    headers = {"X-Auth-Token": ticket}
    url = "https://"+ip+"/api/"+ver+"/"+api
    # print ("\nExecuting GET '%s'\n"%url)
    try:
    # The request and response of "GET /network-device" API
        resp= requests.get(url,headers=headers,params=params,verify = False)
        # print ("GET '%s' Status: "%api,resp.status_code,'\n') # This is the http request status
        return(resp)
    except:
       print ("Something wrong to GET /",api)
       sys.exit()

def post(ip=dnac_config.DNAC_IP,ver=dnac_config.VERSION,uname=dnac_config.USERNAME,pword=dnac_config.PASSWORD,api='',data=''):
    """
    To simplify requests.post with default configuration. Return is the same as requests.post

    Parameters
    ----------
    ip (str): dnac routable DNS addess or ip
    ver (str): dnac VERSION
    uname (str): user name to authenticate with
    pword (str): PASSWORD to authenticate with
    api (str): dnac api without prefix
    data (JSON): JSON object

    Return:
    -------
    object: an instance of the Response object(of requests module)
    """
    ticket = get_X_auth_token(ip,ver,uname,pword)
    headers = {"content-type" : "application/json","X-Auth-Token": ticket}
    url = "https://"+ip+"/api/"+ver+"/"+api
    # print ("\nExecuting POST '%s'\n"%url)
    try:
    # The request and response of "POST" API
        resp = requests.post(url,json.dumps(data),headers=headers,verify = False)
        # print(resp.text)
        # print ("POST '%s' Status: "%api,resp.status_code,'\n') # This is the http request status
        return(resp)
    except:
       print ("Something wrong to POST /",api)
       sys.exit()

def put(ip=dnac_config.DNAC_IP,ver=dnac_config.VERSION,uname=dnac_config.USERNAME,pword=dnac_config.PASSWORD,api='',data=''):
    """
    To simplify requests.put with default configuration.Return is the same as requests.put

    Parameters
    ----------
    ip (str): dnac routable DNS addess or ip
    VERSION (str): dnac VERSION
    USERNAME (str): user name to authenticate with
    PASSWORD (str): PASSWORD to authenticate with
    api (str): dnac api without prefix
    data (JSON): JSON object

    Return:
    -------
    object: an instance of the Response object(of requests module)
    """
    ticket = get_X_auth_token(ip,ver,uname,pword)
    headers = {"content-type" : "application/json","X-Auth-Token": ticket}
    url = "https://"+ip+"/api/"+ver+"/"+api
    # print ("\nExecuting PUT '%s'\n"%url)
    try:
    # The request and response of "PUT" API
        resp= requests.put(url,json.dumps(data),headers=headers,verify = False)
        # print ("PUT '%s' Status: "%api,resp.status_code,'\n') # This is the http request status
        return(resp)
    except:
       print ("Something wrong to PUT /",api)
       sys.exit()

def delete(ip=dnac_config.DNAC_IP,ver=dnac_config.VERSION,uname=dnac_config.USERNAME,pword=dnac_config.PASSWORD,api='',params=''):
    """
    To simplify requests.delete with default configuration.Return is the same as requests.delete

    Parameters
    ----------
    ip (str): dnac routable DNS addess or ip
    ver (str): dnac API VERSION
    uname (str): user name to authenticate with
    pword (str): PASSWORD to authenticate with
    api (str): dnac api without prefix
    params (str): optional parameter for DELETE request

    Return:
    -------
    object: an instance of the Response object(of requests module)
    """
    ticket = get_X_auth_token(ip,ver,uname,pword)
    headers = {"X-Auth-Token": ticket,'content-type': 'application/json'}
    url = "https://"+ip+"/api/"+ver+"/"+api
    # print ("\nExecuting DELETE '%s'\n"%url)
    try:
    # The request and response of "DELETE" API
        resp= requests.delete(url,headers=headers,params=params,verify = False)
        # print ("DELETE '%s' Status: "%api,resp.status_code,'\n') # This is the http request status
        return(resp)
    except:
       print ("Something wrong to DELETE /",api)
       sys.exit()


def prettyPrint(text="", json_object=None):
    """
    Parameters
    ----------
    text (str) : message to print out
    json_object (Response object): an instance of the Response object(of requests module)

    Return:
    -------
    None
    """
    resp = json_object.json() # Get the json-encoded content from response
    print (json.dumps(resp,indent=4))    # This is the entire response from the query



