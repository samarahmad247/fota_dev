import os
import json
import time
import boto3
import zipfile
import requests
import logging
import traceback
from threading import Thread
from threading import Event
from queue import Queue
from common_header import *
from error_codes import *
from json.decoder import JSONDecodeError
from importlib.metadata import metadata

logger = logging.getLogger()

class FOTAHandler():
    def __init__(self, main_obj, wifi_obj, fota_event_arg):
        self.name = "WIFI_MODULE"
        Thread.__init__(self)
        self.WIFIWaitlist = []
        self.mainObject = main_obj
        self.WIFIObject = wifi_obj
        self.FOTAEvent = fota_event_arg
        self.machineUDI = self.FetchKeyFromVersionList(MACHINE_UDI)
        self.currentVersion = self.FetchKeyFromVersionList(CURRENT_VERSION)
        self.s3_client = boto3.client(S3_CLIENT, aws_access_key_id = ACCESS_KEY_AWS,
                                     aws_secret_access_key = SECRET_ACCESS_KEY_AWS)

    def FetchKeyFromVersionList(self, key):
        rKey = ""
        #IMPLEMENT SIGANL BASED TIMEOUT HERE ##################################
        try:
            file = open(VERSION_FILE_PATH, FILE_READ)
            fileData = file.read()
            for line in fileData.strip():
                if key in line:
                    rKey = (line.split("="))[1]
                    break
            file.close()
        except Exception as e:
            logger.error("FOTA module: Failed to open version-list file: Error {0}".format(e))
            logger.error(traceback.format_exc())
        return rKey

    def GetRemoteVersionFromKey(self, key):
        rKey = "0.0.0"
        #check internet
        if self.WIFIObject.CheckInternet():
            ResponseObj = self.PostRequest(self.CreateAPIRqBody(API_GET_NEW_VERSION_NUMBER))
            if ResponseObj != '':
                if ResponseObj.status_code is SUCCESSFUL_RESPONSE_STATUS:
                    rKey = (ResponseObj.json())[DATA][key]
                    pass
                else:
                    logger.debug("FOTA module: Received response contains error status. Response - {0} \
                                , Error - {1}".format(ResponseObj, ResponseObj.status_code))
            else:
                logger.debug("FOTA module: Invalid Response object received. {0}".format(ResponseObj))
        else:
            logger.debug("FOTA module: Failed to check for update. Internet error.")
        return rKey

    def CheckKey(self, rData):
        rStatus = True
        if rData != []:
            if len(rData[BODY]) == API_SET[rData[API]]:
                if rData[API] != API_GET_ALL_VERSION:
                    for field in rData[BODY]: 
                        if len(rData[BODY][field]) != 0:
                            pass
                        else:
                            logger.debug("FOTA module: {0} field missing in API body. API - {1}"\
                                        .format(field,rData[API]))
                            rStatus = False
            else:
                logger.debug("FOTA module: API body for {0} expects {1} fields, only {2} given." \
                            .format(rData[API], API_SET[rData[API]], len(rData[BODY])))
                rStatus = False
        else:
            logger.debug("FOTA module: API request body empty")
            rStatus = False
        return rStatus
    
    def CalcVersionWeightage(self, version_str):
        #version -     1  .   2   .  3
        #weightage - 10^4 + 10^2  + 10^0
        rWeight = 0
        ver_list = version_str.split('.')
        for num in range(3):
            rWeight = rWeight + int(ver_list[num])*(10**(2*(2-num)))
        return rWeight  

    def CheckZIP(self, file_path):
        #implement a timeout here using signal #######################################################################
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.testzip()
                return True
        except zipfile.BadZipFile:
            return False      

    def CreateAPIRqBody(self, api, arg1=EMPTY, arg2=EMPTY):
        rData = []
        if api in API_SET:
            tempData = {}
            if api is API_GET_CURRENT_VERSION:
                tempData[MACHINE_UDI] = self.machineUDI
            if api is API_SAVE_MACHINE_UDI:
                tempData[MACHINE_UDI] = arg1
                tempData[CURRENT_VERSION] = arg2
            if api is API_GET_NEW_VERSION_NUMBER:
                tempData[MACHINE_UDI] = self.machineUDI
            if api is API_UPDATE_VERSION_FROM_DEVICE:
                tempData[MACHINE_UDI] = self.machineUDI
                tempData[SYSTEM_VERSION] = arg1
                tempData[SYSTEM_UPDATE_STATUS] = arg2
            rData[API] = api
            rData[BODY] = tempData
        else:
            logger.debug("FOTA module: undefined API called. Returning empty request.")
        return rData

    def PostRequest(self, rData):
        rStatus = ''
        if self.CheckKey(rData):
            if rData[API] != API_GET_CURRENT_VERSION:
                try:
                    resObject = requests.post(url=(DEFAULT_DOMAIN+rData[API]), 
                                            header=API_HEADER,
                                            json=rData[BODY],
                                            timeout=COMMAND_TIMEOUT)
                    rStatus = resObject
                    return rStatus
                except Exception as e:
                    logger.error("FOTA module: Failed to post API request: Error {0}".format(e))
                    logger.error(traceback.format_exc())
            else:
                try:
                    resObject = requests.get(url=(DEFAULT_DOMAIN+rData[API]), 
                                            header=API_HEADER,
                                            timeout=COMMAND_TIMEOUT)
                    resObject = resObject
                    return rStatus
                except Exception as e:
                    logger.error("FOTA module: Failed to post API request: Error {0}".format(e))
                    logger.error(traceback.format_exc())
        else:
            logger.debug("FOTA module: Key check failed. Exiting PostRequest..")
        return rStatus
    
    def FileWrite(self, key, value):
        rStatus = False
        #IMPLEMENT SIGANL BASED TIMEOUT HERE ##################################
        try:
            file = open(VERSION_FILE_PATH, FILE_READ)
            fileData = file.read()
            for line in fileData.strip():
                if key in line:
                    fileData = fileData.replace(line, key+"="+value)
                    rStatus = True
                    break
            file.close()
            if rStatus:
                try:
                    file = open(VERSION_FILE_PATH, FILE_WRITE)
                    file.write(fileData)
                    file.close()
                except Exception as e:
                    logger.error("FOTA module: Failed to open version-list file: Error {0}".format(e))
                    logger.error(traceback.format_exc())
                    rStatus = False
        except Exception as e:
            logger.error("FOTA module: Failed to open version-list file: Error {0}".format(e))
            logger.error(traceback.format_exc())
            rStatus = False
        return rStatus

    def UpdateMachineUDI(self, queuePacket):
        rStatus = False
        #check internet
        if self.WIFIObject.CheckInternet():
            #Call API to update UDI
            ResponseObj = self.PostRequest(self.CreateAPIRqBody(API_SAVE_MACHINE_UDI, 
                                                                queuePacket[DATA][MACHINE_UDI],
                                                                queuePacket[DATA][CURRENT_VERSION]))
            if ResponseObj != '':
                if ResponseObj.status_code is SUCCESSFUL_RESPONSE_STATUS:
                    #Edit version-list with UDI
                    if self.FileWrite(MACHINE_UDI, queuePacket[DATA][MACHINE_UDI]):
                        self.machineUDI = queuePacket[DATA][MACHINE_UDI]
                        self.currentVersion = queuePacket[DATA][CURRENT_VERSION]
                        rStatus = True
                        pass
                    else:
                        logger.debug("FOTA module: Failed to write machine UDI to file")
                        queuePacket[TASK_ERR] = ERROR_FILE_READ_WRITE_FAILED
                else:
                    logger.debug("FOTA module: Received response contains error status. Response - {0} \
                                , Error - {1}".format(ResponseObj, ResponseObj.status_code))
                    queuePacket[TASK_ERR] = ERROR_CODES_MAP_DASHBOARD[ResponseObj.status_code]
            else:
                logger.debug("FOTA module: Invalid Response object received. {0}".format(ResponseObj))
                queuePacket[TASK_ERR] = ERROR_INVALID_RESPONSE_OBJECT
        else:
            logger.debug("FOTA module: Failed to upadate machine UDI. Internet error.")
            queuePacket[TASK_ERR] = ERROR_CONNECTING_TO_INTERNET
        queuePacket[TASK_TYPE] = RESPONSE
        self.mainObject.DataQueue.put(queuePacket)
        return rStatus

    def CheckUpdate(self, queuePacket):
        rStatus = False
        #check internet
        if self.WIFIObject.CheckInternet():
            ResponseObj = self.PostRequest(self.CreateAPIRqBody(API_GET_NEW_VERSION_NUMBER))
            if ResponseObj != '':
                if ResponseObj.status_code is SUCCESSFUL_RESPONSE_STATUS:
                    queuePacket[DATA] = {SYSTEM_VERSION:(ResponseObj.json())[DATA][SYSTEM_VERSION]}
                    rStatus = True
                    pass
                else:
                    logger.debug("FOTA module: Received response contains error status. Response - {0} \
                                , Error - {1}".format(ResponseObj, ResponseObj.status_code))
                    queuePacket[TASK_ERR] = ERROR_CODES_MAP_DASHBOARD[ResponseObj.status_code]
            else:
                logger.debug("FOTA module: Invalid Response object received. {0}".format(ResponseObj))
                queuePacket[TASK_ERR] = ERROR_INVALID_RESPONSE_OBJECT
        else:
            logger.debug("FOTA module: Failed to check for update. Internet error.")
            queuePacket[TASK_ERR] = ERROR_CONNECTING_TO_INTERNET
        queuePacket[TASK_TYPE] = RESPONSE
        self.mainObject.DataQueue.put(queuePacket)
        return rStatus
    
    def SendRollback(self, queuePacket):
        rStatus = False
        #check internet
        if self.WIFIObject.CheckInternet():
            ResponseObj = self.PostRequest(self.CreateAPIRqBody(API_UPDATE_VERSION_FROM_DEVICE,
                                                                queuePacket[DATA][SYSTEM_VERSION], 
                                                                queuePacket[DATA][SYSTEM_UPDATE_STATUS]))
            if ResponseObj != '':
                if ResponseObj.status_code is SUCCESSFUL_RESPONSE_STATUS:
                    #Edit version-list with UDI
                    if self.FileWrite(SENT_ROLLBACK, ROLLBACK_SUCCESS):
                        self.currentVersion = queuePacket[DATA][SYSTEM_VERSION]
                        rStatus = True
                        pass
                    else:
                        logger.debug("FOTA module: Failed to write machine UDI to file")
                        queuePacket[TASK_ERR] = ERROR_FILE_READ_WRITE_FAILED
                else:
                    logger.debug("FOTA module: Received response contains error status. Response - {0} \
                                , Error - {1}".format(ResponseObj, ResponseObj.status_code))
                    queuePacket[TASK_ERR] = ERROR_CODES_MAP_DASHBOARD[ResponseObj.status_code]
            else:
                logger.debug("FOTA module: Invalid Response object received. {0}".format(ResponseObj))
                queuePacket[TASK_ERR] = ERROR_INVALID_RESPONSE_OBJECT
        else:
            logger.debug("FOTA module: Failed to send rollback update. Internet error.")
            queuePacket[TASK_ERR] = ERROR_CONNECTING_TO_INTERNET
        queuePacket[TASK_TYPE] = RESPONSE
        self.mainObject.DataQueue.put(queuePacket)
        return rStatus

    def Update(self, queuePacket):
        rStatus = True
        failure_count = RESET
        download_count = RESET
        iomtOs_present = RESET
        updateVersion = queuePacket[DATA][SYSTEM_VERSION].split(".")
        currentVersion = self.FetchKeyFromVersionList(CURRENT_VERSION).split(".")
        for file in range(0,4):
            if updateVersion[file] > currentVersion[file]:
                logger.debug("FOTA module: Newer version {0} available for {1}. Downloading..."
                             .format(updateVersion[file], SYSTEM_VERSION_SEQ[file]))
                if self.Download(SYSTEM_VERSION_SEQ[file], queuePacket[DATA][SYSTEM_VERSION], 
                                 updateVersion[file]):
                    download_count = download_count + 1
                    logger.debug("FOTA module: Download successful.")
                    if SYSTEM_VERSION_SEQ[file] == IOMT_OS_DIR:
                        iomtOs_present = SET
                else:
                    logger.debug("FOTA module: Download failed.")
                    failure_count = failure_count + 1
        if failure_count > 0:
            rStatus = False
            logger.debug("FOTA module: Failed to download few packages.")
            queuePacket[TASK_ERR] = ERROR_DOWNLOADING_PACKAGE
            queuePacket[TASK_TYPE] = RESPONSE
            self.mainObject.DataQueue.put(queuePacket)
            return rStatus
        if failure_count is RESET and download_count != RESET:
            if iomtOs_present is SET:
                #perform update of OS

    def Download(self, file_type, sys_update_ver, version):
        rStatus = False
        #check internet
        if self.WIFIObject.CheckInternet():
            #Select the file map
            mapList = S3_FILE_MAP[file_type]
            for file in mapList:
                #Fetch local and remote files and download if needed
                localVersion = self.FetchKeyFromVersionList[FILE_TO_VERSION_MAP[file]]
                remoteVersion = self.GetRemoteVersionFromKey(FILE_TO_VERSION_MAP[file])
                if self.CalcVersionWeightage(remoteVersion) > self.CalcVersionWeightage(localVersion):
                    s3_object_key = file_type + SLASH + version + SLASH  + file + remoteVersion + DOT_ZIP        
                    metadata=self.s3_client.head_object(Bucket=S3_BUCKET, Key=s3_object_key) 
                    total_length=int(metadata.get('ContentLength', 0))

                    def progress(chunk):
                        print(chunk)
                        self.downloaded += chunk 
                        print("downloaded from cloud = ",self.downloaded)
                        done = int(100 * self.downloaded / total_length)
                        print("done=",done)
                                            
                    logger.info(f'Downloading {s3_object_key}')
                    #create path if not exists 
                    localDIRpath = LOCAL_DOWNLOAD_PATH + sys_update_ver + SLASH + file_type 
                    try:
                        os.makedirs(localDIRpath, exist_ok=True)
                        localPath = localDIRpath + SLASH + file + remoteVersion + DOT_ZIP
                        #download
                        with open(localPath, 'wb') as self.file_object:
                            self.s3_client.download_fileobj(S3_BUCKET, s3_object_key, 
                                                            self.file_object, Callback=progress)
                        #Check zip file
                        if self.CheckZIP(localPath):
                            logger.info("FOTA module: File downloaded successfully.")
                            rStatus = True
                        else:
                            logger.debug("FOTA module: Downloaded ZIP file {} corrupted."
                                        .format(file + remoteVersion + DOT_ZIP))
                    except Exception as e:
                        logger.error("FOTA module: Failed to download remote {0} file. \
                                    Error {1}".format((file + remoteVersion), e))
                        logger.error(traceback.format_exc())
        else:
            logger.debug("FOTA module: Failed to download update. Internet error.")
        return rStatus