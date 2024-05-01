# Anonymize Data

## Introduction

This is a Python-based utility that automates the process of managing and processing data files within specific categories and subfolders. It provides efficient data handling by converting text files to CSV, anonymizing file names, modifying file creation dates, and scheduling these operations automatically. Inital purpose of this script was to anonymize OpenBCI brainwave data recorded from students as to hide indentity. 

### Features

- **File Conversion**: Converts text files to CSV format, facilitating easier data analysis.
- **File Anonymization**: Anonymizes file names and modification times to enhance privacy and security.
- **Scheduled Tasks**: Automates tasks via cron jobs, allowing operations to run at specified intervals.
- **Data Handling**: Supports recursive handling of subdirectories for comprehensive file processing.
- **Logging and Monitoring**: Tracks the steps and changes made during file processing, providing detailed logs for audit and review.

### System Requirements

Script Automation System leverages Python and several third-party libraries to automate and schedule file processing tasks efficiently.

## Installation

1. Clone the project to your local machine and navigate to the project directory.
2. Set up a Python virtual environment:
   
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the necessary Python libraries:
   
   ```
   pip install pandas python-crontab
   ```

4. Configure system permissions for script execution by modifying the sudoers file to allow the script to change system time and manage system services without requiring a password:
   
   ```
   sudo vi /etc/sudoers.d/your-config-file
   # Add the following lines:
   ALL ALL = (ALL) NOPASSWD: /bin/date, /usr/bin/systemctl
   ```

5. Run the script to automate data processing:
   
   ```
   python main.py
   ```

Ensure that the paths and schedules are correctly set in the `config.py` file before running the script.
