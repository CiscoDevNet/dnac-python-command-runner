import ast # use it for converting string to dict
import time # Need it for delay - sleep() function
from dnac import * # common functions in danc.py


def select_device_id():
    """
    This function returns a network device id that user selected from a list.
    Exit script if there is no any network device.

    Parameters
    ----------
    NONE

    Return:
    -------
    list: network device ip and id
    """
    device=[]
    # Create a list of network devices
    try:
        resp = get(api="network-device")
        status = resp.status_code
        response_json = resp.json() # Get the json-encoded content from response
        device = response_json["response"] # The network-device
    except:
        print ("Something wrong, cannot get network device information")
        sys.exit()

    if status != 200:
        print ("Response status %s,Something wrong !"%status)
        print (resp.text)
        sys.exit()

    if device == []:
        print ("Oops! No device was found ! Discover network device first.")
        sys.exit()

    device_list = []
    # Extracting attributes and add a counter to an iterable
    idx=0
    for item in device:
        idx+=1
        device_list.append([str(idx),item["hostname"],item["managementIpAddress"],item["type"],item["instanceUuid"]])
    if device_list == []:
        print ("There is no network-device can be used to run command !")
        sys.exit()
    # Pretty print tabular data, needs 'tabulate' module
    print (tabulate(device_list, headers=['number','hostname','ip','type'],tablefmt="rst"),'\n')

    # Ask user's selection
    # Find out network device with selected ip or hostname, index 4 is the network device id
    # In the loop until 'id' is assigned or user enter 'exit'
    device_ip_idx = 2 # Network device ip index in the list
    device_id_idx = 4 # Network device id index in the list
    net=[]
    while True:
        user_input = input('Select a number for the device from the list to run IOS command: ')
        user_input= user_input.lstrip() # Ignore leading space
        if user_input.lower() == 'exit':
            sys.exit()
        if user_input.isdigit(): # Make sure user's input in in range
            if int(user_input) in range(1,len(device_list)+1):
                net.append(device_list[int(user_input)-1][device_ip_idx]) # The device_ip_idx is the position of ip
                net.append(device_list[int(user_input)-1][device_id_idx])
                return net
            else:
                print ("Oops! number is out of range, please try again or enter 'exit'")
        else:
            print ("Oops! input is not a digit, please try again or enter 'exit'")
    # End of while loop

def run_command(net,cmd_list,cmd_str):
    """
    This function returns the output of IOS command
    Exit script if there is no any network device.

    Parameters
    ----------
    net (list): network device ip andid
    cmd_list (list): available IOS commands in list
    cmd (string): available IOS commands in string

    Return:
    -------
    str: output of running IOS command
    """

    # getting command input
    while True:
        cmd = input('\n=> Enter IOS command you like to run on this device, ip='+net[0]+' or "exit" to exit: ')
        cmd = cmd.lstrip() # Ignore leading space
        cmd = cmd.lower()  # to lower case
        if cmd == 'exit':
            sys.exit()
        elif cmd == "": # no input
            print ("Oops! command cannot be NULL please try again or enter 'exit'")
        elif cmd.split(' ')[0] not in cmd_list: # retrieve the first word of command string
            print("Invalid command, valid commands are the following (some of them maybe not available in certain devices) : ",cmd_str,'\n')
        else:
            break

    # JOSN for posting IOS command
    cmd_json = {
        "commands" : [cmd],
        "deviceUuids" : [net[1]]  # net = [ip,deviceid]
        }
    try:
       # print (cmd_json)
       # print("\nExecuting \"",cmd,"\" please wait ........\n\n")
       resp = post(api="network-device-poller/cli/read-request", data=cmd_json)
       # prettyPrint(resp)
       response_json = resp.json()
       taskId=response_json["response"]["taskId"]
    except:
       print ("\n For some reason cannot get taskId")
       sys.exit()
    else:
        r = get(api="task/"+taskId)
        response_json = r.json()
        progress = response_json["response"]["progress"]
        count = 0
        # We can only see fileId when tsak is finished
        while "fileId" not in progress:
            try:
                r = get(api="task/"+taskId)
                response_json = r.json()
                progress = response_json["response"]["progress"]
            except:
            # Something is wrong
                print ("\nSomething is wrong when executing get task/"+taskId)
                sys.exit()
            time.sleep(1)
            count += 1
            if count > 20: # timeout after ~20 seconds
                print ("\nTaking too long, script time out!")
                return ("Error")
                sys.exit()
        # convert string to dict
        p=ast.literal_eval(progress)
        fileid=p["fileId"]

    # now retrieve the output of running IOS command


    r = get(api="file/"+fileid)
    response_json = r.json()
    # real output

    if response_json[0]["commandResponses"]["FAILURE"] != {}:
        print (response_json[0]["commandResponses"]["FAILURE"][cmd])
    else:
        try:
            output = response_json[0]["commandResponses"]["SUCCESS"][cmd]
            print (output)
            return output
        except:
        # Something is wrong
            if cmd.split(' ')[1] == '?':
                output = response_json[0]["commandResponses"]["FAILURE"][cmd]
                print (output)
            else:
                print ("Response from get task\n",json.dumps(response_json,indent=4))
                print ("\nSomething is wrong when parsing the command output")
                return ("Error")
                sys.exit()


if __name__ == "__main__": # Execute only if run as a script

    try:
        r = get(api="network-device-poller/cli/legit-reads") # "get" - Function in dnac.py
        response_json = r.json()
        cmd_list=response_json["response"]
        # convert list to a string
        cmd_str=', '.join(cmd_list)

    except:
        # Something is wrong
        print ("\nSomething is wrong to get legit-reads")
        sys.exit()
    netid = select_device_id() # getting network device id
    while True:
        run_command(netid,cmd_list,cmd_str)



