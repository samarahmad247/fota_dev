import logging
import traceback
import queue
from threading import Thread
from threading import Event
from queue import Queue
import time
from datetime import datetime
import socket
import zmq
import secrets
from common_header import *
from error_codes import *
import json
from json.decoder import JSONDecodeError

logger = logging.getLogger()

class Communication_Handler():
    def __init__(self, main_obj, rx_event_arg, tx_event_arg):
        self.name = "COMMUNICATION_FOTA"
        Thread.__init__(self)
        self.mainObject = main_obj
        self.RxEvent = rx_event_arg
        self.TxEvent = tx_event_arg
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, bytes(FOTA_IOMT_DEALER_ID_STR, 'utf-8'))
        # Make connect call with the Router 
        try:
            self.socket.connect(ROUTER_SOCKET_ADDRESS)
            self.PacketList = {}
            self.RxEvent.set()
            logging.debug("ZMQ connect request sent, dealerID: {0} socketID: {1}" \
                            .format(FOTA_IOMT_DEALER_ID, zmq.IDENTITY))
        except:
            logging.error("Error creating ZMQ socket connnection")
    
    def SendData(self, dJSONMsg):
        try:
            logger.info("Tx thread: >>>  {}".format(dJSONMsg))
            #Convert JSON message dictonary to string
            json_obj_to_send = json.dumps(dJSONMsg)
            self.socket.send_multipart([b'1', bytes(json_obj_to_send,'utf-8')])
            logger.info("JSON message sent to the Router")
            return SUCCESS
        except Exception as e:
            logger.error("Tx thread: Failed to send JSON message: {0} error: {1}".format(dJSONMsg,e))
            logger.error(traceback.format_exc())
            return FAILED

    def CreatePacket(self, module, task, task_type, data):
        Packet = {}
        Packet[UUID]     = secrets.token_hex(8)
        Packet[MODULE]   = module
        Packet[TASK]     = task
        Packet[TASK_TYPE]= task_type
        Packet[TASK_ERR] = NO_ERROR
        Packet[DATA]     = data
        return Packet
    
    def SendPacket(self, queuePacket):
        SPacket = {}
        SPacket[SOURCE_KEY]       = FOTA_IOMT_DEALER_ID
        SPacket[DESTINATION_KEY]  = self.PacketList[queuePacket[UUID]][SOURCE]
        SPacket[MESSAGE_TYPE_KEY] = queuePacket[TASK]
        SPacket[STATUS_KEY]       = queuePacket[TASK_ERR]
        SPacket[DATA_KEY]         = queuePacket[DATA] 
        return SPacket

    def RxHandler(self):
        while True:
            #check for event from main
            if self.RxEvent.is_set():
                logging.debug("Main requested a stop event. Exiting Rx thread...")
                break
            #receive data and parse

            logger.debug("Rx thread: Entered Rx thread infinite loop")
            # Blocking zmq received call 
            self.socket.recv()
            received_data = self.socket.recv()

            logger.info("Rx Thread: <<< {0}".format(received_data))

            try:
                dJSONMsg = json.loads(received_data)
            except JSONDecodeError as e:
                logger.error("Rx thread: JSON parsing failed: {0}".format(e))
                logger.error(traceback.format_exc())

            if MESSAGE_TYPE_KEY in dJSONMsg:
                Source = dJSONMsg[SOURCE_KEY]
                if dJSONMsg[MESSAGE_TYPE_KEY] == MSG_TYPE_HEART_BEAT:
                    dJSONMsg.clear() 
                    dJSONMsg = self.CreatePacket(TRANSMIT, MSG_TYPE_HEART_BEAT, RESPONSE, EMPTY)
                    self.PacketList[dJSONMsg[UUID]] = {}
                    self.PacketList[dJSONMsg[UUID]][CREATEDAT] = int(round(datetime.now().timestamp()))
                    self.PacketList[dJSONMsg[UUID]][SOURCE] = Source
                    self.mainObject.TxQueue.put(dJSONMsg)
                    

                elif dJSONMsg[MESSAGE_TYPE_KEY] == MESSAGE_TYPE_WITH_DATA:
                    MessageType = dJSONMsg[MESSAGE_TYPE_KEY]
                    DATA = dJSONMsg[DATA_KEY]
                    dJSONMsg.clear()
                    if MessageType in MSG_TYPE_WIFI:
                        dJSONMsg = self.CreatePacket(WIFI, MessageType, REQUEST, DATA)
                    if MessageType in MSG_TYPE_FOTA:
                        dJSONMsg = self.CreatePacket(FOTA, MessageType, REQUEST, DATA)
                    self.mainObject.DataQueue.put(dJSONMsg)
                    self.PacketList[dJSONMsg[UUID]] = {}
                    self.PacketList[dJSONMsg[UUID]][CREATEDAT] = int(round(datetime.now().timestamp()))
                    self.PacketList[dJSONMsg[UUID]][SOURCE] = Source

                elif dJSONMsg[MESSAGE_TYPE_KEY] in MESSAGE_TYPE_NO_DATA:
                    MessageType = dJSONMsg[MESSAGE_TYPE_KEY]
                    dJSONMsg.clear()
                    if MessageType in MSG_TYPE_WIFI:
                        dJSONMsg = self.CreatePacket(WIFI, MessageType, REQUEST, EMPTY)
                    if MessageType in MSG_TYPE_FOTA:
                        dJSONMsg = self.CreatePacket(FOTA, MessageType, REQUEST, EMPTY)
                    self.mainObject.DataQueue.put(dJSONMsg)
                    self.PacketList[dJSONMsg[UUID]] = {}
                    self.PacketList[dJSONMsg[UUID]][CREATEDAT] = int(round(datetime.now().timestamp()))
                    self.PacketList[dJSONMsg[UUID]][SOURCE] = Source
                logger.info("Rx thread: Packet List - {}".format(self.PacketList))
        
    def TxHandler(self):
        #Set initialization with router
        dJSONMsg = {}
        dJSONMsg[SOURCE_KEY] = FOTA_IOMT_DEALER_ID
        dJSONMsg[DESTINATION_KEY] = ROUTER_ID
        dJSONMsg[MESSAGE_TYPE_KEY] = MSG_TYPE_REG
        dJSONMsg[DATA_KEY] = {}
        self.SendData(dJSONMsg)
        while True:
            dJSONMsg = {}
            #check for event from main
            if self.TxEvent.is_set():
                logging.debug("Main requested a stop event. Exiting Tx thread...")
                break
            
            logger.debug("Tx thread: Entered Tx thread infinite loop")

            #Check packet list for unaddressed packets
            for key in self.PacketList.copy():
                ElapsedTime = (int(round(datetime.now().timestamp())) - self.PacketList[key][CREATEDAT])
                if  ElapsedTime >= PACKETLIST_MAX_WAIT_TIME: 
                    logger.info("Tx thread: Rx Packet not serviced. \
                                UUID {0} elapsed time {1}".format(key, ElapsedTime))
            #pop data from tx queue
            try:
                dJSONMsg = self.mainObject.TxQueue.get(block=True, 
                            timeout=QUEUE_DATA_FETCH_TIMEOUT)
                logger.info("Tx thread: <<< {0}".format(dJSONMsg))
            except queue.Empty:
                pass
            except Exception as e:
                logger.error("Tx thread: Failed to fetch packet from Tx queue. Error: {0}".format(e))
                logger.error(traceback.format_exc())
            
            try:                                
                if(type(dJSONMsg) is dict) and dJSONMsg != {}:
                    logger.info("Tx thread: Received packet {}".format(dJSONMsg))
                    
                    if (dJSONMsg.get(UUID) is not None) and (dJSONMsg[UUID] in self.PacketList):
                            if self.SendData(self.SendPacket(dJSONMsg)):
                                try:
                                    del self.PacketList[dJSONMsg[UUID]]
                                    logger.info("Tx thread: Packet List - {}".format(self.PacketList))
                                    logger.debug("Tx thread: UUID {0} serviced, \
                                                    clearing from packetlist".format(dJSONMsg[UUID]))
                                except  Exception as e:
                                    logger.error("Tx thread: Unable to remove UUID {0} from packetlist.\
                                                    Error: {1}".format(dJSONMsg[UUID],e))
                                    logger.error(traceback.format_exc())
                            dJSONMsg.clear()
                    else:
                        logger.info("Tx thread: <<< Invalid packet pushed to Tx queue.\
                                    UUID mismatch. Packet - {0}".format(dJSONMsg))

            except Exception as e:
                logger.error("Tx thread: JSON parsing failed: {0}".format(e))
                logger.error(traceback.format_exc())    
                
    
    def run(self):
        #Initiate Rx Thread
        self.RxThread = Thread(target=self.RxHandler)
        self.RxThread.start()
        logging.debug("Rx thread started")

        #Initiate Tx Thread
        self.TxThread = Thread(target=self.TxHandler)
        self.TxThread.start()
        logging.debug("Tx thread started")