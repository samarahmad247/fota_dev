import sys
import time
import queue
import logging
import logging.handlers
import traceback
from queue import Queue
from threading import Thread
from threading import Event
from common_header import *
from wifi import WifiHandler
from communication import Communication_Handler

"""
Function: logging_setup
Description: This function setup the logging for the Application. This function takes the 
values from the logging_types dictonary. based on that it will decide where applicaiton logs 
should be print on colsole and logging file
"""
def logging_setup():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Print the logs in to the console, if "log_into_console" key is true
    if logging_types['log_into_console'] == True:
        ch = logging.StreamHandler(sys.stdout)
        # TODO: Here developer can decide the log level which will be print over the console
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    # Store the logs in to the file if "log_into_file" key is true
    if logging_types['log_into_file'] == True:
        log_file_handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, 
                                                                maxBytes = LOG_FILE_SIZE, 
                                                                backupCount = LOG_FILE_BACK_COUNT)
        # TODO: Here developer can decide the log level which will stored in to the log file
        log_file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_file_handler.setFormatter(formatter)
        root.addHandler(log_file_handler)
    return root

class Task_Handler():
    def __init__(self):
        self.name = "MAIN_FOTA"
        Thread.__init__(self)
        #Logging setup
        self.logger = logging_setup()
        
        #Initialize Communication handlers 
        self.RxHandleEvent = Event()
        self.TxHandleEvent = Event()
        self.CommHandle = Communication_Handler(self, self.RxHandleEvent, self.TxHandleEvent)
        if self.RxHandleEvent.wait(timeout=COMMAND_TIMEOUT):
            self.RxHandleEvent.clear()
            self.DataQueue = Queue()
            self.TxQueue = Queue()
            self.CommHandle.run()
            logger.info("Main Thread: Initialized Communication Handler")
        else:
            logging.error("Main thread: Cannot initiate Coomunication threads. \
                          RxEvent: {0}, TxEvent: {1}".format(self.RxHandleEvent, self.TxHandleEvent))        
        
        #Initialize WIFI handler  
        self.WifiHandleEvent = Event()
        self.WifiHandle = WifiHandler(self, self.WifiHandleEvent)
        logger.info("Main Thread: Initialized WIFI Handler")

    def InsertToWaitlist(self, list, entry):
        if len(list) < WAITLIST_LENGTH:
            #append to list
            list.insert(FIRST_ENTRY, entry)
        else: 
            logger.info("Main Thread: {} full. Waiting for list elements to process..".format(list))

    def GetFromWaitlist(self, list):
        rTask = {}
        if len(list) > 0:
            rTask = list.pop(LAST_ENTRY)
        else:
            logger.info("Main Thread: {} empty. Waiting for tasks.".format(list))
        return rTask
    
    def work(self):
        while True:
            #get data from queue and parse
            try:
                dJSONMsg = {}
                dJSONMsg = self.DataQueue.get(block=True, 
                                timeout=QUEUE_DATA_FETCH_TIMEOUT)
                logger.info("Main Thread: Received message - {0}".format(dJSONMsg))     

                if(type(dJSONMsg) is dict) and dJSONMsg != {}:
                    if dJSONMsg[MODULE] == WIFI:
                        #Add task to wifi waitlist
                        self.InsertToWaitlist(WIFI_MODULE_WAITLIST, dJSONMsg)
                    if dJSONMsg[MODULE] == FOTA:
                        #Add task to FOTA waitlist  
                        self.InsertToWaitlist(FOTA_MODULE_WAITLIST, dJSONMsg)
            except queue.Empty:
                pass
            except Exception as e:
                logger.error("Main thread: Failed to fetch packet from Tx queue. Error: {0}".format(e))
                logger.error(traceback.format_exc())
            #cases 
            wifiTask = {}
            wifiTask = self.GetFromWaitlist(WIFI_MODULE_WAITLIST)
            if wifiTask != {}:
                logger.info("Main Thread: wifiTask - {}".format(wifiTask)) 
                if wifiTask[TASK_TYPE] == RESPONSE:
                    #Todo: additional check can be added to control the tasks assigned to threads.
                    self.TxQueue.put(wifiTask)
                if wifiTask[TASK_TYPE] == REQUEST:
                    if wifiTask[TASK] == MSG_TYPE_WIFI_LIST:
                        if self.WifiHandle.WiFiScan(wifiTask):
                            logger.info("Main Thread: Successful in fetching wifi list") 
                        else:
                            logger.info("Main Thread: Failure in getting wifi list")     
                    if wifiTask[TASK] == MSG_TYPE_WIFI_CONNECT:
                        if self.WifiHandle.WiFiConnect(wifiTask):
                            logger.info("Main Thread: Successful in connecting to wifi network") 
                        else:
                            logger.info("Main Thread: Failure in connecting to wifi network") 
                    if wifiTask[TASK] == MSG_TYPE_WIFI_OFF:
                        if self.WifiHandle.WiFiOFF(wifiTask):
                            logger.info("Main Thread: Successful in turning off wifi") 
                        else:
                            logger.info("Main Thread: Failure in turning off wifi") 
                    if wifiTask[TASK] == MSG_TYPE_CONNECTED_WIFI_NAME:
                        if self.WifiHandle.GetCurrentWiFiSSID(wifiTask):
                            logger.info("Main Thread: Successful in fetching wifi SSID wifi") 
                        else:
                            logger.info("Main Thread: Failure in fetching wifi SSID wifi") 
            fotaTask = {}
            fotaTask = self.GetFromWaitlist(FOTA_MODULE_WAITLIST)
            if fotaTask != {}:
                logger.info("Main Thread: fotaTask - {}".format(fotaTask)) 
                if fotaTask[TASK_TYPE] == RESPONSE:
                    #Todo: additional check can be added to control the tasks assigned to threads.
                    self.TxQueue.put(fotaTask)

logger = logging_setup()
taskHandler = Task_Handler()
taskHandler.work()