import threading
import subprocess 
import sys
import time
import socket
import os
import zipfile
import shutil
from distutils.dir_util import copy_tree
import stat

def install_package():
        strSourcePath = '/home/kapure/noccarc/Kapure_work/mark_2/Work/development_files/ota_dev/FOTA_improvements/replace_file.py'
        strDestinationPath = '/home/kapure/noccarc/Kapure_work/mark_2/Work/development_files/ota_dev/FOTA_improvements/test_codes_python/replace_file.py'
        shutil.copy(strSourcePath, strDestinationPath)
        print("replaced file")
install_package()
    

