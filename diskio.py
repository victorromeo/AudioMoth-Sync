from configuration import configuration as config
import logging
logging.basicConfig(filename='logs/activity.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

import shutil
import sys
from shell import output_shell

class diskio:
    def check_disk(self, report):
        total, used, free = shutil.disk_usage("/")

        if (report):
            logging.debug("Disk Total:%d",total)
            logging.debug("Disk Used:%d",used)
            logging.debug("Disk Free:%d",free)

        print("Total: %d MB" % (total // (2**20)))
        print("Used:  %d MB" % (used // (2**20)))
        print("Free:  %d MB" % (free // (2**20)))
        print("Avail: %0.2f %%" % (free / total))

        if ((free / total) < config.min_disk_percent or (free < config.min_disk_mb)):
            print("Insufficient disk space remaining")
            logging.error("Insufficient disk space remaining %d %d", free, total)
            sys.exit()
    
    def transfer_audio(self, moth_mount_path:str, audio_path:str):

        listMothFilesCommand = "ls -la {0}/*.WAV".format(moth_mount_path)
        syncFilesCommand = "rsync -r {0}/ {1}".format(moth_mount_path, audio_path)
        removeMothFilesCommand = "rm {0}/*.WAV".format(moth_mount_path)

        logging.info("Fetching AudioMoth files list")
        files, success = output_shell(listMothFilesCommand)

        if (success):
            logging.info(", ".join(files))
            logging.info("Transferring AudioMoth to Local")
            result, success = output_shell(syncFilesCommand)

            if (success):
                logging.info("Transfer complete")
                result, success = output_shell(removeMothFilesCommand)

                if (success):
                    logging.info("AudioMoth files removed")
                else:
                    logging.warning("Failed to remove AudioMoth files")
            else:
                logging.warning("Failed to transfer files")
        else:
            logging.warning("Failed to fetch AudioMoth files")