import logging
import traceback
import subprocess 
from common_header import *
from error_codes import *
from threading import Thread
from threading import Event
from queue import Queue
import time
import urllib.request

logger = logging.getLogger()

class WifiHandler():
    def __init__(self, main_obj, wifi_event_arg):
        self.name = "WIFI_MODULE"
        Thread.__init__(self)
        self.WIFIWaitlist = []
        self.mainObject = main_obj
        self.WIFIEvent = wifi_event_arg
        if self.InitWiFiOFF():
            logger.info("Wifi Module: Wifi turned off during init of wifi handler.")

    def ProcessTimeoutCheck(self, CurrTime, queuePacket):
        if (time.perf_counter() - CurrTime) > PROCESS_TIMEOUT:
            queuePacket[TASK_ERR] = ERROR_THREAD_PROCESS_TIMEOUT
            queuePacket[TASK_TYPE] = RESPONSE
            self.mainObject.DataQueue.put(queuePacket)
            return True
        else:
            return False
    
    def CheckInternet(self):
        try:
            #Request a url 
            urllib.request.urlopen(CHECK_INTERNET_HOST, timeout=COMMAND_TIMEOUT)
            return True
        except Exception as e:
            logger.error("Wifi Module: Failed to check internet connectivity. Check route table.\
                          Error {0}".format(e))
            logger.error(traceback.format_exc())
            return False
        
    def CheckWIFIStatus(self):
        rStatus = False
        try:
            strCommand = "nmcli radio wifi"
            byteOutPut = subprocess.check_output(strCommand, shell=True, timeout=COMMAND_TIMEOUT)
            decodedString = byteOutPut.decode('utf-8').strip()
            if decodedString in WIFI_ENABLE_STATUS:
                logger.info("Wifi Module: Wifi is enabled")
                rStatus = True
            else:
                logger.debug("Wifi Module: Wifi is disabled")
        except Exception as e:
            logger.error("Wifi Module: Failed to check wifi status. Error {0}".format(e))
            logger.error(traceback.format_exc())
        return rStatus
    
    def GetCurrentWiFiSSID(self, queuePacket):
        # If there is no wifi connection then this function will return -- string
        rStatus = FAILED
        strCurrentWiFiName = "--"
        check_count = WIFI_CONNECTION_RETRY_COUNT
        CurrTime = time.perf_counter()
        try:
            logger.info("Wifi Module: Checking WIFI status.")
            while (check_count > 0):
                #Timeout block
                if self.ProcessTimeoutCheck(CurrTime, queuePacket):
                    return rStatus
                if self.CheckWIFIStatus():
                    rStatus = SUCCESS
                    break
                else:
                    logger.info("Wifi Module: Trying to turn on WIFI..")
                    subprocess.check_output("nmcli radio wifi on", shell=True)
                    time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS*4)
                    check_count = check_count - 1

            if self.CheckWIFIStatus():
                strCommand = "iw dev wlan0 info | grep ssid | awk '{for (i=2; i<NF; i++) printf($i\" \");\
                                print $NF}'"
                byteOutPut = subprocess.check_output(strCommand, shell=True, timeout=COMMAND_TIMEOUT)
                decodedString = byteOutPut.decode('utf-8').strip()
                if decodedString != "":
                    strCurrentWiFiName = decodedString
                    rStatus = SUCCESS
                else:
                    queuePacket[TASK_ERR] = ERROR_WIFI_NOT_CONNECTED_TO_NETWORK
            else:
                logger.debug("Wifi Module: Unable to turn on WIFI")
                queuePacket[TASK_ERR] = ERROR_TURNING_WIFI_ON
        except Exception as e:
            logger.error("Wifi Module: Failed to get the current wifi name error: {0}".format(e))
            logger.error(traceback.format_exc())
            queuePacket[TASK_ERR] = ERROR_FETCHING_SSID

        logger.debug("Wifi Module: Current connection > {0}".format(strCurrentWiFiName))
        queuePacket[DATA] = {WIFI_NAME_KEY:strCurrentWiFiName}
        queuePacket[TASK_TYPE] = RESPONSE
        self.mainObject.DataQueue.put(queuePacket)
        return rStatus
    
    def WiFiScan(self, queuePacket):
        rStatus = FAILED
        check_count = WIFI_CONNECTION_RETRY_COUNT
        lWiFiListOfAPListObjects = []
        CurrTime = time.perf_counter()
        try:
            logger.info("Wifi Module: Checking WIFI status.")
            while (check_count > 0):
                #Timeout block
                if self.ProcessTimeoutCheck(CurrTime, queuePacket):
                    return rStatus
                if self.CheckWIFIStatus():
                    rStatus = SUCCESS
                    break
                else:
                    logger.info("Wifi Module: Trying to turn on WIFI..")
                    subprocess.check_output("nmcli radio wifi on", shell=True, timeout=COMMAND_TIMEOUT)
                    time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS*4)
                    check_count = check_count - 1

            if self.CheckWIFIStatus():
                lWiFiList = []
                process = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'],\
                                        stdout=subprocess.PIPE, timeout=COMMAND_TIMEOUT)
                if process.returncode == 0:
                    result =  process.stdout.decode('utf-8').strip().split('\n')
                
                # parse the command output and prepare the wifi list for each access points
                for each in result:
                    if not each.startswith(":"):
                        data = each.split(":")
                        if(False == any(data[0] in i for i in lWiFiList)):
                            lWiFiList.append(data)
                            lWiFiListOfAPListObjects.append({SSID_KEY:data[0], SECURITY_KEY:data[1],\
                                                            SIGNAL_KEY:int(data[2])})

                logger.debug("Wifi Module: Access points data in list: {}".format(lWiFiListOfAPListObjects))
                rStatus = SUCCESS
            else:
                logger.debug("Wifi Module: Unable to turn on WIFI")
                queuePacket[TASK_ERR] = ERROR_TURNING_WIFI_ON
                
        except Exception as e:
            logger.error("Wifi Module: Failed to fetch the wifi list, error: {1}".format(e))
            logger.error(traceback.format_exc())
            queuePacket[TASK_ERR] = ERROR_FETCHING_WIFI_LIST
        
        queuePacket[DATA] = {ACCESS_POINT_LIST_ARRAY_KEY : lWiFiListOfAPListObjects}
        queuePacket[TASK_TYPE] = RESPONSE
        self.mainObject.DataQueue.put(queuePacket)
        return rStatus

    def InitWiFiOFF(self):
        rStatus = FAILED
        iStatus = ERROR_TURNING_WIFI_OFF
        check_count = WIFI_CONNECTION_RETRY_COUNT
        CurrTime = time.perf_counter()
        try:
            logger.info("Wifi Module: Checking WIFI status.")
            while (check_count > 0):
                #Timeout block
                if (time.perf_counter() - CurrTime) > PROCESS_TIMEOUT:
                    return rStatus
                if False == self.CheckWIFIStatus():
                    rStatus = SUCCESS
                    break
                else:
                    logger.info("Wifi Module: Trying to turn off WIFI..")
                    subprocess.check_output("nmcli radio wifi off", shell=True, timeout=COMMAND_TIMEOUT)
                    time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS*4)
                    check_count = check_count - 1

            if self.CheckWIFIStatus():
                logger.debug("Wifi Module: Unable to turn off WIFI")
            else:
                rStatus = SUCCESS
        except Exception as e:
            logger.error("Wifi Module: Failed to turn off the wifi: {0}".format(e))
            logger.error(traceback.format_exc())   
        return rStatus
        
    def WiFiOFF(self, queuePacket):
        rStatus = FAILED
        iStatus = ERROR_TURNING_WIFI_OFF
        check_count = WIFI_CONNECTION_RETRY_COUNT
        CurrTime = time.perf_counter()
        try:
            logger.info("Wifi Module: Checking WIFI status.")
            while (check_count > 0):
                #Timeout block
                if self.ProcessTimeoutCheck(CurrTime, queuePacket):
                    return rStatus
                if False == self.CheckWIFIStatus():
                    rStatus = SUCCESS
                    break
                else:
                    logger.info("Wifi Module: Trying to turn off WIFI..")
                    subprocess.check_output("nmcli radio wifi off", shell=True, timeout=COMMAND_TIMEOUT)
                    time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS*4)
                    check_count = check_count - 1

            if self.CheckWIFIStatus():
                logger.debug("Wifi Module: Unable to turn off WIFI")
                queuePacket[TASK_ERR] = ERROR_TURNING_WIFI_OFF
            else:
                rStatus = SUCCESS
        except Exception as e:
            logger.error("Wifi Module: Failed to turn off the wifi: {0}".format(e))
            logger.error(traceback.format_exc())  
        queuePacket[TASK_TYPE] = RESPONSE 
        self.mainObject.DataQueue.put(queuePacket)
        return rStatus

    def WiFiConnect(self, queuePacket):
        rStatus = False
        wifi_connect_retry = WIFI_CONNECTION_RETRY_COUNT
        current_wifi_name = {}
        dummy_packet = {}
        CurrTime = time.perf_counter()
        try:
            current_wifi_name = self.GetCurrentWiFiSSID(dummy_packet)

            # If new wifi name is same as connected wifi then just check internet 
            # connectivity, No need to connect again
            if(((current_wifi_name[DATA][WIFI_NAME_KEY] == queuePacket[DATA][SSID_KEY]) \
                and (True == self.CheckInternet()))):
                rStatus = SUCCESS
            else:
                # wait for some time between two commands 
                time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS)

                #If wifi is connected with some network, need to disconnect first
                if(current_wifi_name[DATA][WIFI_NAME_KEY] != "--"):
                    logger.info("Wifi Module: Currently, wifi is connected with {}"\
                                .format(current_wifi_name[DATA][WIFI_NAME_KEY]))

                    #down the current wifi connection
                    strOutput = subprocess.check_output("nmcli c down id " + '"' + \
                                                        current_wifi_name[DATA][WIFI_NAME_KEY] + '"', \
                                                        shell=True, timeout=COMMAND_TIMEOUT)
                    logger.debug("Wifi Module: Output of current wifi down command: {0}".format(strOutput))

                    time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS)

                    subprocess.call(['nmcli', 'd', 'disconnect', 'wlan0'], timeout=COMMAND_TIMEOUT)

                while(wifi_connect_retry > 0):
                    #Timeout block
                    if self.ProcessTimeoutCheck(CurrTime, queuePacket):
                        return rStatus
                    # wait for some time between two commands 
                    time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS)  
                    # Make wifi connect call
                    subprocess.call(['nmcli', 'd', 'wifi', 'connect', queuePacket[DATA][SSID_KEY], \
                                     'password', queuePacket[DATA][PASSWORD_KEY]], timeout=COMMAND_TIMEOUT)
                    
                    current_wifi_name = {}
                    current_wifi_name = self.GetCurrentWiFiSSID(dummy_packet)
                    
                    # break the loop if wifi connected
                    if((current_wifi_name[DATA][WIFI_NAME_KEY] == queuePacket[DATA][SSID_KEY]) 
                       and (True == self.CheckInternet())):
                        rStatus = SUCCESS
                        break
                    else:
                        logger.info("Wifi Module: Turning OFF and turning ON the wifi interface")
                        strCommand = "nmcli radio wifi off"
                        subprocess.check_output(strCommand, shell=True, timeout=COMMAND_TIMEOUT)
                        time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS)
                        strCommand = "nmcli radio wifi on"
                        subprocess.check_output(strCommand, shell=True, timeout=COMMAND_TIMEOUT)
                        time.sleep(WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS*4)

                    wifi_connect_retry = wifi_connect_retry - 1
                
                current_wifi_name = {}
                current_wifi_name = self.GetCurrentWiFiSSID(dummy_packet)
                # check for the internet after successfull wifi connection    
                if(current_wifi_name[DATA][WIFI_NAME_KEY] == queuePacket[DATA][SSID_KEY]):
                    if(False == self.CheckInternet()):
                        queuePacket[TASK_ERR] = ERROR_CONNECTING_TO_INTERNET
                    else:
                        rStatus = SUCCESS
                else:
                    queuePacket[TASK_ERR] = ERROR_CONNECTING_TO_WIFI
        except Exception as e:
            logger.error("Wifi Module: Failed to connect with wifi: {0}".format(e))
            logger.error(traceback.format_exc())
            queuePacket[TASK_ERR] = ERROR_CONNECTING_TO_WIFI

        queuePacket[DATA] = {WIFI_NAME_KEY:current_wifi_name[DATA][WIFI_NAME_KEY]}
        queuePacket[TASK_TYPE] = RESPONSE
        self.mainObject.DataQueue.put(queuePacket)
        return rStatus