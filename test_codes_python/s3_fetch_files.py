from importlib.metadata import metadata
from urllib import response
import boto3
import sys
import os
import time
import datetime
import logging
from botocore.config import Config
from boto3.dynamodb.conditions import Key, Attr


access_key = 'AKIAYLQ34C3L3I7FQ4TD'
secret_access_key = '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'


class OTAupdate:
    def __init__(self) -> None:
        self.aws_access_key_id=access_key
        self.aws_secret_access_key=secret_access_key
        self.local_download_path="/home/kapure/Documents/softwarefiles/firmware/1.2.1.zip"
        self.s3_bucket='otapackages'
        self.region_name='ap-south-1'     
        self.s3_client=boto3.client('s3', aws_access_key_id = self.aws_access_key_id, aws_secret_access_key =self.aws_secret_access_key)
        self.file_extension=".zip"
        self.strLatestPkgName = ""
        self.strLatestPkgVersion = ""
        self.file_objec=""
        self.downloaded=0
        self.file_size=0

    def download(self):

        s3_object_key = "firmware/2/Master_1.2.1.zip"
        bReturn = False

        metadata=self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_object_key) 
        total_length=int(metadata.get('ContentLength', 0))
        print("total file length = ",total_length)

        def progress(chunk):
            print(chunk)
            self.downloaded += chunk 
            print("downloaded from cloud = ",self.downloaded)
            # time.sleep(1)
            done = int(100 * self.downloaded / total_length)
            print("done=",done)
            #sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
            #sys.stdout.flush()
            #if(done==100):
            # 
            
        print(f'Downloading {s3_object_key}')
        print(self.local_download_path)
        with open(self.local_download_path, 'wb') as self.file_objec:
            self.s3_client.download_fileobj(self.s3_bucket, s3_object_key, self.file_objec, Callback=progress)

        # downloadprogress()
        print("downloaded_fileSize=",os.path.getsize(self.local_download_path))
        bReturn = True
        
        return bReturn

a = OTAupdate()
a.download()