#!/usr/bin/env python3
import os
import shutil
import tarfile
from datetime import datetime
import logging

# Directories for storing backups
BACKUP_DIR = os.path.expanduser("~/Desktop/python/Backup/ALLBackups")
COMPRESSED_BACKUP_DIR = os.path.expanduser("~/Desktop/python/Backup/compressed_BackUps")
LOG_FILE = os.path.expandvars("$HOME/Desktop/python/logfiles/system_monitor_{log_date}.log")

# Create backup directories if they don't exist
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(COMPRESSED_BACKUP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_message(message):
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = LOG_FILE.format(log_date=log_date)
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(message)s')
    logging.info(message)

def search_item(search_path):
    """Search for a file or directory. Handle both absolute and relative paths."""
    if os.path.exists(search_path):
        return os.path.abspath(search_path)
    
    log_message(f"No such file or directory found: {search_path}")
    raise FileNotFoundError(f"No such file or directory found: {search_path}")

def backup_file(file_name):
    """Backup a file."""
    file_path = search_item(file_name)
    log_message(f"Start Backup file: {file_path}")
    print(f"Start Backup file: {file_path}")

    if not os.path.isfile(file_path):
        log_message(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name_only = os.path.basename(file_path)
    file_basename, file_extension = os.path.splitext(file_name_only)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file_path = os.path.join(BACKUP_DIR, f"{file_name_only}_backup_{timestamp}{file_extension}")
    compressed_file_path = os.path.join(COMPRESSED_BACKUP_DIR, f"{file_basename}_backup_{timestamp}.tar.gz")

    try:
        # Copy file to backup directory
        shutil.copy2(file_path, backup_file_path)
        log_message(f"Backup created: {backup_file_path}")
        print(f"Backup created: {backup_file_path}")

        # Compress the backup
        with tarfile.open(compressed_file_path, "w:gz") as tar:
            tar.add(backup_file_path, arcname=os.path.basename(backup_file_path))
        log_message(f"Compressed backup created: {compressed_file_path}")
        print(f"Compressed backup created: {compressed_file_path}")



    except Exception as e:
        log_message(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
        raise

    log_message(f"Done Backup file: {file_path}")
    print(f"Done Backup file: {file_path}")

def backup_directory(dir_name):
    """Backup a directory."""
    dir_path = search_item(dir_name)
    log_message(f"Start Backup directory: {dir_path}")
    print(f"Start Backup directory: {dir_path}")

    if not os.path.isdir(dir_path):
        log_message(f"Directory not found: {dir_path}")
        raise NotADirectoryError(f"Directory not found: {dir_path}")

    dir_name_only = os.path.basename(dir_path)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir_path = os.path.join(BACKUP_DIR, f"{dir_name_only}_backup_{timestamp}")
    compressed_dir_path = os.path.join(COMPRESSED_BACKUP_DIR, f"{dir_name_only}_backup_{timestamp}.tar.gz")

    try:
        # Copy directory to backup directory
        shutil.copytree(dir_path, backup_dir_path)
        log_message(f"Backup created: {backup_dir_path}")
        print(f"Backup created: {backup_dir_path}")

        # Compress the backup
        with tarfile.open(compressed_dir_path, "w:gz") as tar:
            tar.add(backup_dir_path, arcname=os.path.basename(backup_dir_path))
        log_message(f"Compressed backup created: {compressed_dir_path}")
        print(f"Compressed backup created: {compressed_dir_path}")

    except Exception as e:
        log_message(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
        raise

    log_message(f"Done Backup directory: {dir_path}")
    print(f"Done Backup directory: {dir_path}")

def main(option,path):

    if option == '-f':
            backup_file(path)

    elif option == '-d':
            backup_directory(path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py [-f file_name | -d dir_name]")
        sys.exit(1)

    option = sys.argv[1]
    path   = sys.argv[2]
    main(option ,path)

