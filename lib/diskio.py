import shutil
import sys
from lib.config import cfg
from lib.log import logging
from lib.shell import output_shell
import os

class diskio:
    def check_disk(self, report = True, display = True, path:str = "/"):
        total, used, free = shutil.disk_usage(path)

        if (report):
            logging.info(f"Disk at {path} (Total:{total} Used:{used} Free:{free})")

        if (display):
            gb = (2**20)
            print(f"Disk at {path} (Total:{total // gb} Used:{used // gb} Free:{free // gb} Avail:{(free * 100/total):.2f})")

        return total, used, free, (free/total) * 100
        
        # if ((free / total) < cfg.health.min_disk_percent or (free < cfg.health.min_disk_mb)):
        #     print("Insufficient disk space remaining")
        #     logging.error("Insufficient disk space remaining %d %d", free, total)
        #     sys.exit()

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

    def remove_files(self, path:str, pattern:str = "*.WAV", sudo:bool = False):
        logging.info(f"Removing files from '{path}/{pattern}'")
        actor = 'sudo ' if sudo else ''
        removeMothFilesCommand = f"{actor}rm -f {path}/{pattern}"
        _, success = output_shell(removeMothFilesCommand)

        if success:
            logging.info("Removal complete")

        return success

    def transfer_audio(self, moth_mount_path:str, audio_path:str):

        if self.list_files(moth_mount_path) \
            and self.sync_files(moth_mount_path, audio_path) \
                and self.remove_files(moth_mount_path, pattern = '*.WAV', sudo = True):
            logging.info("Transfer complete")
        else:
            logging.warning("Transfer failed")

    def format_partition_fat32(self, moth_mount_path:str):

        target_device= os.popen("lsblk -l -f | grep vfat | grep sd | grep Moth | awk \'{print $1}\'").read()

        if moth_mount_path == f'/dev/{target_device}' and moth_mount_path.starts_with('/dev/sd'):
            _, success = output_shell(f'sudo mkfs.vfat -F 32 {moth_mount_path}')
            return success

        return False

    def is_mounted(self, device_path):
        find_mount_command = f"mount | grep -F '{device_path}' | cut -d \" \" -f 3"
        mount_path, success = output_shell(find_mount_command)

        mount_path = mount_path[:-1] if (success and len(mount_path) > 3) else None

        return success, mount_path

    def mount_device(self, device_path: str, mount_path: str):
        print(f'Mounting {device_path} at {mount_path}')
        #r, success = output_shell(f'sudo mount -o rw,remount {device_path} {mount_path}')
        r, success = output_shell(f'sudo mount {device_path} {mount_path}')


        if not success:
            print(f'Mount failed: {r}', flush=True)

        return success

    def unmount_device(self, device_path: str):
        r, success = output_shell(f'sudo umount {device_path}')

        if not success:
            print(f'Unmount failed: {r}')
        
            parent_device_path = device_path.rstrip('1234567890')
            r, success = output_shell(f'sudo eject {parent_device_path}')
        
        return success
    
    def get_md5(self, path):
        return output_shell(f"md5sum {path} | awk '{{print $1}}'")

    def exists(self, path):
        return os.path.exists(path)
    
    def sendmail(subject:str, message:str, to:str):
        output_shell(f"echo '{message}' | mail -s '{subject}' {to}")