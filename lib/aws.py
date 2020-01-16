import sys
sys.path.append("..") # Adds higher directory to python modules path.

from configuration import configuration as config

import os
from datetime import datetime
from shell import output_shell
from typing import List 

class aws:

    def Execute(self, command):
        result, success = output_shell(command)
        return result, success

    def Copy(self, from_path:str, to_path:str, recursive:bool = False):
        command = "aws s3 cp {0} {1} {2}".format(from_path, to_path, '--recursive' if recursive else '').strip()
        result, success = self.Execute(command)
        return result, success

    def Sync(self, from_path:str, to_path:str, recursive:bool = False):
        command = "aws s3 sync {0} {1} {2}".format(from_path,to_path, '--recursive' if recursive else '').strip()
        result, success = self.Execute(command)
        return result, success

    def MakeBucket(self, bucket):
        command = "aws s3 mb {0}".format(bucket)
        result, success = self.Execute(command)
        return result, success

    def RemoveBucket(self, bucket, force:bool = False):
        command = "aws s3 rb {0} {1}".format(bucket, '--force' if force else '').strip()
        result, success = self.Execute(command)
        return result, success

    def List(self, path:str):
        command = "aws s3 ls {0}".format(path)
        result, success = self.Execute(command)
        return result, success

    def Move(self, from_path:str, to_path:str, quiet:bool = True, include:str = None, exclude:str = None):
        include_condition = '--include={0}'.format(include) if include is not None else ''
        exclude_condition = '--exclude={0}'.format(exclude) if exclude is not None else ''

        command = "aws s3 mv {0} {1} {2} {3} {4}".format(from_path, to_path, '--quiet' if quiet else '', include_condition, exclude_condition).strip()
        result, success = self.Execute(command)
        return result, success