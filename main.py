"""
Author: Brendan Kariniemi
Description: This script will recursively and randomly reformat files from a given directory to maintain anonymity
while also converting all txt files into csv format.
"""

import datetime
import random
import shutil
import pathlib
import subprocess
import uuid
import os
import logging
import config
import pandas as pd
from crontab import CronTab

# Init logging
logging.basicConfig(
    filename=config.output_log,
    level=logging.INFO,
    format='[%(levelname)s] - %(message)s'
)


# Attempts to remove a directory specified by dir_name.
def remove_directory(dir_name):
    shutil.rmtree(dir_name)


# Returns a random timestamp from within the last 10 days.
def get_random_timestamp():
    now = datetime.datetime.now()
    ten_days_ago = now - datetime.timedelta(days=10)
    random_timestamp = datetime.datetime.fromtimestamp(random.uniform(ten_days_ago.timestamp(), now.timestamp()))
    return random_timestamp.strftime('%m%d%H%M%Y.%S')


# Moves files from source_dir to dest_dir,
# recursively handling subdirectories and deleting empty source directories.
def extract_files(source_dir, dest_dir):
    for item in source_dir.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            # If it is a file, just move it.
            # Rename copy to uid in order to handle files already named as a number.
            uid = uuid.uuid4()
            file_extension = item.suffix
            shutil.copy(item, dest_dir / f"{uid}{file_extension}")
            # Delete the original
            item.unlink()
        elif item.is_dir():
            # Recursively extract subdirectories
            extract_files(item, dest_dir)
            # Delete the directory after extracting
            remove_directory(item)


# Converts all txt files in dirname into csv format
def convert_txt_files(dir_name):
    for file in dir_name.iterdir():
        if file.is_file() and not file.name.startswith('.') and file.suffix == '.txt':
            header_lines = []
            csv_file = dir_name / f"{file.stem}.csv"

            with open(file, 'r') as infile:
                for _ in range(5):
                    header_lines.append(infile.readline())
                df = pd.read_csv(infile)

            with open(csv_file, 'w') as outfile:
                for line in header_lines:
                    outfile.write(line)

            # Write the DataFrame to the CSV file
            df.to_csv(csv_file, index=False, mode='a')
            file.unlink()


# Renames files in dir_name from 1 to N, where N is the number of files in the directory.
def rename_files(dir_name):
    # Generate a list of unique random numbers from 1 to N and shuffle them
    files = [file for file in dir_name.iterdir() if file.is_file() and not file.name.startswith('.')]
    num_files = len(files)
    random_numbers = list(range(1, num_files + 1))
    random.shuffle(random_numbers)

    # Apply new names to files
    for file, num in zip(files, random_numbers):
        file_extension = file.suffix
        new_path = dir_name / f"{num}{file_extension}"
        file.rename(new_path)


# Logs the names and creation times of files in dir_name.
def display_files(dir_name):
    for item in dir_name.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            file_name = item.name
            creation_time = datetime.datetime.fromtimestamp(item.stat().st_ctime)
            logging.info(f"{file_name} - {creation_time}")
        elif item.is_dir():
            # Recurse
            display_files(item)


# Orchestrates the processing of a directory.
def process_directory(dir_name):
    # Step 1: Display files before modifying names and dates
    logging.info(f"{dir_name} files before changes:")
    display_files(dir_name)

    # Step 2: Extract files
    extract_files(dir_name, dir_name)

    # Step 3: Rename files
    rename_files(dir_name)

    # Step 4: Convert txt files to csv
    convert_txt_files(dir_name)

    # Step 5: Display files after renaming and date change
    logging.info(f"{dir_name} files after changes:")
    display_files(dir_name)


def change_time():
    date_time = get_random_timestamp()
    subprocess.run(['sudo', 'systemctl', 'stop', 'systemd-timesyncd'])
    subprocess.run(['sudo', 'date', date_time])


def resync_time():
    subprocess.run(['sudo', 'systemctl', 'start', 'systemd-timesyncd'])


# Set up a cronjob to execute this script automatically
def setup_cron():
    script_path = os.path.abspath(__file__)
    cron = CronTab(user=True)
    cron_command = f"{config.python_path} {script_path} >> {config.output_log} 2>&1"

    for job in cron:
        if job.is_valid() and job.command == cron_command:
            # Update job
            job.setall(config.cron_schedule)
            cron.write()
            break
    else:
        # If the script is not in the crontab, add it
        job = cron.new(command=cron_command)
        job.setall(config.cron_schedule)
        cron.write()


def main():
    # Change the time to a random date
    change_time()

    directory_path = pathlib.Path(config.input_path)

    if directory_path.exists() and directory_path.is_dir():
        sub_dirs = [item for item in directory_path.iterdir() if item.is_dir()]
        for sub_dir in sub_dirs:
            process_directory(sub_dir)
    else:
        logging.error(f"The directory {directory_path} does not exist.")

    logging.info('Data reformatting complete!')

    # Make sure time is back to normal
    resync_time()

    # Setup chron to run automatically
    setup_cron()


if __name__ == '__main__':
    main()
