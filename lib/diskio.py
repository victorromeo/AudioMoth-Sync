from lib.config import cfg
from lib.log import logging

import shutil
import sys
from shell import output_shell

class diskio:
    def check_disk(self, report = True, display = True):
        total, used, free = shutil.disk_usage("/")

        if (report):
            logging.debug("Disk Total:%d",total)
            logging.debug("Disk Used:%d",used)
            logging.debug("Disk Free:%d",free)

        if (display):
            print("Total: %d MB" % (total // (2**20)))
            print("Used:  %d MB" % (used // (2**20)))
            print("Free:  %d MB" % (free // (2**20)))
            print("Avail: %0.2f %%" % (free / total))

        if ((free / total) < cfg.health.min_disk_percent or (free < cfg.health.min_disk_mb)):
            print("Insufficient disk space remaining")
            logging.error("Insufficient disk space remaining %d %d", free, total)
            sys.exit()

    def create_folder(self, path: str):
        logging.info("Create Folder '{0}'".format(path))
        createFolderCommand = "mkdir {0}".format(path)
        _, success = output_shell(createFolderCommand)

        if success:
            logging.info("Create Folder successful")
        else:
            logging.info("Create Folder unsuccessful")

    def remove_folder(self, path:str):
        logging.info("Remove Folder '{0}'".format(path))
        createFolderCommand = "rm -rf {0}".format(path)
        _, success = output_shell(createFolderCommand)

        if success:
            logging.info("Remove Folder successful")
        else:
            logging.info("Remove Folder unsuccessful")

    def list_files(self, path:str, pattern: str = "*.WAV"):
        listMothFilesCommand = "ls -1Ap {0}/{1}".format(path, pattern)
        logging.info("Fetching files list in '{0}/{1}'".format(path, pattern))
        files, success = output_shell(listMothFilesCommand)
        fileList = [] if files is None else files.splitlines()

        if success and len(fileList) > 0:
            logging.info("Recordings count {0}".format(len(fileList)))
            logging.info(", ".join(fileList))
        else:
            logging.warning("No recordings found")
            return False

        return success
    
    def sync_files(self, from_path:str, to_path:str):
        logging.info("Transferring AudioMoth to Local")
        syncFilesCommand = "rsync -r {0}/ {1}".format(from_path, to_path)
        _, success = output_shell(syncFilesCommand)

        if success:
            logging.info("Transfer complete")
        
        return success

    def remove_files(self, path:str, pattern:str = "*.WAV"):
        logging.info("Removing files from '{0}/{1}'".format(path, pattern))
        removeMothFilesCommand = "rm {0}/{1}".format(path, pattern)
        _, success = output_shell(removeMothFilesCommand)

        if success:
            logging.info("Removal complete")
        
        return success

    def transfer_audio(self, moth_mount_path:str, audio_path:str):

        if self.list_files(moth_mount_path) and self.sync_files(moth_mount_path, audio_path) and self.remove_files(moth_mount_path):
            logging.info("Transfer complete")
        else:
            logging.warning("Transfer failed")