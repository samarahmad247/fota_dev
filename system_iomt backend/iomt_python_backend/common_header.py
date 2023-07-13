SET = 1
RESET = 0
SUCCESS = 1
FAILED = 0
CONNECTED = 0
FOTA_IOMT_DEALER_ID = 4
FOTA_IOMT_DEALER_ID_STR = '4'
ROUTER_SOCKET_ADDRESS = "tcp://192.168.0.1:5555"
logging_types = {"log_into_console":True, "log_into_file" : True}

LOG_FILE_NAME = "iomt_python_backend.txt"
LOG_FILE_SIZE = 1024 * 1024 * 2
LOG_FILE_BACK_COUNT = 3

RX_THREAD_ID = 2
TX_THREAD_ID = 3

SOURCE_KEY='source'
DESTINATION_KEY='destination'
MESSAGE_TYPE_KEY='type'
STATUS_KEY = 'status'
DATA_KEY='data_key'
ERROR_KEY = "error_key"
DATA_FIELD = "data_field"

ROUTER_ID = 1
BACKEND_DEALER_ID = 2
MSG_TYPE_REG = 1
MSG_TYPE_HEART_BEAT = 2

MSG_TYPE_WIFI_LIST = 3
MSG_TYPE_WIFI_CONNECT  = 4
MSG_TYPE_WIFI_OFF = 14
MSG_TYPE_CONNECTED_WIFI_NAME = 13
MSG_TYPE_WIFI = [MSG_TYPE_WIFI_LIST, MSG_TYPE_WIFI_CONNECT, 
                 MSG_TYPE_WIFI_OFF, MSG_TYPE_CONNECTED_WIFI_NAME]

MSG_TYPE_NEW_UPDATE_CHECK = 5
MSG_TYPE_PKG_UPGRADE = 6
MSG_TYPE_PKG_INFO = 7
MSG_TYPE_PKG_ROLLBACK = 8
MSG_TYPE_NEW_PKG_AVAILABLE = 10
MSG_TYPE_ROLLBACK_FEEDBACK = 15
MSG_TYPE_UDI_UPDATE_TO_DASHBOARD = 19
MSG_TYPE_FOTA = [MSG_TYPE_NEW_UPDATE_CHECK, MSG_TYPE_PKG_UPGRADE,
                 MSG_TYPE_PKG_INFO, MSG_TYPE_PKG_ROLLBACK, MSG_TYPE_NEW_PKG_AVAILABLE,
                 MSG_TYPE_ROLLBACK_FEEDBACK, MSG_TYPE_UDI_UPDATE_TO_DASHBOARD]


MESSAGE_TYPE_NO_DATA = [MSG_TYPE_NEW_UPDATE_CHECK,MSG_TYPE_PKG_UPGRADE, 
                        MSG_TYPE_PKG_ROLLBACK, MSG_TYPE_ROLLBACK_FEEDBACK,
                        MSG_TYPE_WIFI_LIST, MSG_TYPE_CONNECTED_WIFI_NAME,
                        MSG_TYPE_WIFI_OFF]

MESSAGE_TYPE_WITH_DATA = [MSG_TYPE_WIFI_CONNECT, MSG_TYPE_UDI_UPDATE_TO_DASHBOARD]

ACCESS_POINT_LIST_ARRAY_KEY = "ap_list"
SOURCE_KEY='source'
DESTINATION_KEY='destination'
MESSAGE_TYPE_KEY='type'
STATUS_KEY = 'status'
DATA_KEY='data'
PKG_TYPE_KEY = 'pkg_type'
PKG_VERSION_KEY = 'version'
PKG_NAME_KEY = "name"
PKG_SIZE_KEY = "size"
PKG_MD5SUM_TAR_KEY = "md5sum_tar"
PKG_MD5SUM_UI_KEY = "md5sum_ui"
PKG_LOCATION_KEY = "location"
SSID_KEY = "ssid"
SECURITY_KEY = "security"
SIGNAL_KEY = "signal"
PASSWORD_KEY = "password"
WIFI_STATUS_KEY = "status"
WIFI_NAME_KEY = "name"

#--------------------Task Handler parameters---------------------------
UUID = "uuid"
MODULE = "module"
TASK = "task"
TASK_TYPE = "task_type"
DATA = "data"
CREATEDAT = "createdat"
SOURCE = "source"
TASK_ERR = "task_error"

WAITLIST_LENGTH = 5
FIRST_ENTRY = 0
LAST_ENTRY = -1

WIFI = "wifi"
FOTA = "fota"
WIFI_MODULE_WAITLIST = []
FOTA_MODULE_WAITLIST = []
REQUEST = "request"
RESPONSE = "response"
TRANSMIT = "transmit"
EMPTY = {}


QUEUE_DATA_FETCH_TIMEOUT = 10
PACKETLIST_MAX_WAIT_TIME = 60

CHECK_INTERNET_HOST = 'http://google.com'
WIFI_CONNECTION_RETRY_COUNT = 3
WAIT_IN_SEC_BETWEEN_WIFI_COMMANDS = 2
WIFI_ENABLE_STATUS = "enabled"

CHECK_INTERNET_COUNT = 3

COMMAND_TIMEOUT = 10
PROCESS_TIMEOUT = 300


#-------------------Dashboard parameters---------------------------
DEFAULT_DOMAIN = "http://ec2-52-66-237-61.ap-south-1.compute.amazonaws.com:8080/admindashboard/machineApi/" 
API_GET_ALL_VERSION = "getAllVersionNumber"
API_GET_CURRENT_VERSION = "getCurrentVersionNumber"
API_SAVE_MACHINE_UDI = "saveMachineUDINumber"
API_GET_NEW_VERSION_NUMBER = "getNewVersionNumber"
API_UPDATE_VERSION_FROM_DEVICE = "updateVersionFromdevice"
#API set -  API : Number of Fields
API_SET = {API_GET_ALL_VERSION : 0, 
           API_GET_CURRENT_VERSION : 1,
           API_SAVE_MACHINE_UDI : 2,
           API_GET_NEW_VERSION_NUMBER : 1,
           API_UPDATE_VERSION_FROM_DEVICE : 3}
API_SECRET_KEY="6bd610eb914a375eb71fcd0ac4650f8c86601f5b6ad9791cdccdfc517f961e96"
API_HEADER = {"Content-Type": "application/json; charset=utf-8",
              'Authorization': API_SECRET_KEY}

#API body parameters
MACHINE_UDI = "machineUDI"
CURRENT_VERSION = "currentVersion"
SYSTEM_VERSION = "systemVersion"
SYSTEM_UPDATE_STATUS = "systemUpdateStatus"

API = 0
BODY = 1

SUCCESSFUL_RESPONSE_STATUS = 200

SYSTEM_VERSION_SEQ = {3:"iomtOs",
                      2:"stmOs",
                      1:"firmware",
                      0:"software"}

#------------------Version file parameters--------------------------
VERSION_FILE_PATH = ""
FILE_WRITE = "w"
FILE_READ = "r"
ROLLBACK_AVAILABLE = "1"
ROLLBACK_SUCCESS = "1"

MACHINE_UDI = "machineUDI"
SYSTEM_VERSION = "systemVersion"
HMI_UI_VERSION = "hmiUiVersion"
HMI_BACKEND_VERSION = "hmiBackendVersion"
FIRMWARE_MASTER_VERSION = "fMasterVersion"
FIRMWARE_SLAVE_VERSION = "fSlaveVersion"
STM_PYTHON_APP_VERSION = "stmPyAppVersion"
STM_C_APP_VERSION = "stmCAppVersion"
STM_OS_VERSION = "stmOsVersion"
IOMT_PYTHON_APP_VERSION = "iomtPyAppVersion"
IOMT_C_APP_VERSION = "iomtCAppVersion"
IOMT_OS_VERSION = "iomtOsVersion"
ROLLBACK_AVAILABLE = "rollbackAvailable"
ROLLBACK_SYS_VERSION = "rollbackVersion"
ROLLBACK_FIRMWARE_VERSION = "rollbackFirmwareVersion"
ROLLBACK_SOFT_VERSION = "rollbackSoftVersion"
SENT_ROLLBACK = "sentRollback"

#------------------s3 bucket parameters--------------------------
S3_CLIENT = 's3'
ACCESS_KEY_AWS = 'AKIAYLQ34C3L3I7FQ4TD'
SECRET_ACCESS_KEY_AWS = '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'
S3_BUCKET = 'otapackages'
LOCAL_DOWNLOAD_PATH = '/home/root/OTA_packages/'
DOT_ZIP = '.zip'
SLASH = '/'

FIRMWARE_DIR = 'firmware'
SOFTWARE_DIR = 'software'
STM_OS_DIR = 'stmOs'
IOMT_OS_DIR = 'iomtOs'

F_MASTER_FILE = 'Master_'
F_SLAVE_FILE = 'Slave_'
F_FILE_LIST = [F_MASTER_FILE, F_SLAVE_FILE]

S_BE_FILE = 'BE_'
S_UI_FILE = 'UI_'
S_FILE_LIST = [S_BE_FILE, S_UI_FILE]

SOS_CAPP_FILE = 'CAPP_'
SOS_INSTALL_FILE = 'Install'
SOS_OS_FILE = 'OS_'
SOS_PYTHON_FILE = 'PY_'
SOS_FILE_LIST = [SOS_CAPP_FILE, SOS_INSTALL_FILE, SOS_OS_FILE, SOS_PYTHON_FILE]

IOMTOS_CAPP_FILE = 'CAPP_'
IOMTOS_INSTALL_FILE = 'Install'
IOMTOS_OS_FILE = 'OS_'
IOMTOS_PYTHON_FILE = 'PY_'
IOMTOS_FILE_LIST = [IOMTOS_CAPP_FILE, IOMTOS_INSTALL_FILE, IOMTOS_OS_FILE, IOMTOS_PYTHON_FILE]

S3_FILE_MAP = {FIRMWARE_DIR : F_FILE_LIST,
               SOFTWARE_DIR : S_FILE_LIST,
               STM_OS_DIR : SOS_FILE_LIST,
               IOMT_OS_DIR : IOMTOS_FILE_LIST}

FILE_TO_VERSION_MAP = {F_MASTER_FILE : FIRMWARE_MASTER_VERSION,
                       F_SLAVE_FILE : FIRMWARE_SLAVE_VERSION,
                       S_BE_FILE : HMI_BACKEND_VERSION,
                       S_UI_FILE : HMI_UI_VERSION,
                       SOS_CAPP_FILE : STM_C_APP_VERSION,
                       SOS_OS_FILE : STM_OS_VERSION,
                       SOS_PYTHON_FILE : STM_PYTHON_APP_VERSION,
                       IOMTOS_CAPP_FILE : IOMT_C_APP_VERSION,
                       IOMTOS_OS_FILE : IOMT_OS_VERSION,
                       IOMTOS_PYTHON_FILE : IOMT_PYTHON_APP_VERSION}