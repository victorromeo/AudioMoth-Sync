from configuration import configuration as config
import logging
logging.basicConfig(filename='logs/activity.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

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

        if ((free / total) < config.min_disk_percent or (free < config.min_disk_mb)):
            print("Insufficient disk space remaining")
            logging.error("Insufficient disk space remaining %d %d", free, total)
            sys.exit()

    def _list_audio_files(self, moth_mount_path:str):
        listMothFilesCommand = "ls -1Ap {0}/*.WAV".format(moth_mount_path)
        logging.info("Fetching AudioMoth files list")
        files, success = output_shell(listMothFilesCommand)
        fileList = [] if files is None else files.splitlines()

        if success and len(fileList) > 0:
            logging.info("Recordings count {0}".format(len(fileList)))
            logging.info(", ".join(fileList))
        else:
            logging.warning("No recordings found")
            return False

        return success
    
    def _sync_audio_files(self, moth_mount_path:str, audio_path:str):
        logging.info("Transferring AudioMoth to Local")
        syncFilesCommand = "rsync -r {0}/ {1}".format(moth_mount_path, audio_path)
        result, success = output_shell(syncFilesCommand)

        if success:
            logging.info("Transfer complete")
        
        return success

    def _remove_moth_files(self, moth_mount_path:str):
        logging.info("Removing files from Moth")
        removeMothFilesCommand = "rm {0}/*.WAV".format(moth_mount_path)
        result, success = output_shell(removeMothFilesCommand)

        if success:
            logging.info("Removal complete")
        
        return success

    def transfer_audio(self, moth_mount_path:str, audio_path:str):

        if self._list_audio_files(moth_mount_path) and self._sync_audio_files(moth_mount_path, audio_path) and self._remove_moth_files(moth_mount_path):
            logging.info("Transfer complete")
        else:
            logging.warning("Transfer failed")