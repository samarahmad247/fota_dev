import requests
import json

# defining the api-endpoint
#get_url = "http://ec2-52-66-237-61.ap-south-1.compute.amazonaws.com:8080/admindashboard/machineapi/getAllVersionNumber"

#current machine version
post_url = "http://ec2-52-66-237-61.ap-south-1.compute.amazonaws.com:8080/admindashboard/machineApi/getNewVersionNumber"

#save machine udi
#post_url = "http://ec2-52-66-237-61.ap-south-1.compute.amazonaws.com:8080/admindashboard/machineapi/saveMachineUDINumber" 

#post_url = "http://ec2-52-66-237-61.ap-south-1.compute.amazonaws.com:8080/admindashboard/machineApi/updateVersionFromdevice"
# your API key here
API_SECRET_KEY="6bd610eb914a375eb71fcd0ac4650f8c86601f5b6ad9791cdccdfc517f961e96"

headers = {"Content-Type": "application/json; charset=utf-8",
           'Authorization': API_SECRET_KEY}
# data to be sent to api
# data = {"machineUDI":"123456789ABCDEF-6",
#         "currentVersion":"1.1.20.1"}
data =  {"machineUDI":"123456789ABCDEF-66666666",
        "systemVersion":"1.1.20.1",
        "systemUpdateStatus":"successful"} 
data = {"machineUDI":"123456789"}
# sending post request and saving response as response object
r1 = requests.post(url=post_url, headers=headers, json=data) 
#print("api get result: {}".format((r1.json())['data']['systemVersion']))
print("status {}".format(r1))

# r = requests.post(url=post_url, data=data)
# # extracting response text
# pastebin_url = r.text
# print("The pastebin URL is:%s" % pastebin_url)