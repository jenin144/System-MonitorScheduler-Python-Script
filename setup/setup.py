import argparse
import os
import subprocess
from datetime import datetime, timedelta
from backup import main as backup_main
from monitoring import main as monitoring_main
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
import logging
import time
import daemon
from apscheduler.triggers.cron import CronTrigger

# Define path templates
log_file_template = os.path.expandvars("$HOME/Desktop/python/logfiles/system_monitor_{log_date}.log")
report_file_template = os.path.expandvars("$HOME/Desktop/python/system_reports/System_Performance_Report_{report_date}.txt")

# Path for the FIFO file
FIFO_FILE = '/tmp/scheduler_fifo'
#*****************************************

def report():
    logging.info("Runningggg the report task")
    monitoring_main(2)  # Call the main function from monitoring script with argument 1


def monitoring():
    logging.info("Running the monitoring task")
    monitoring_main(1)  # Call the main function from monitoring script with argument 1

def backup(option , path):
    logging.info("Running the backup scheduled task")
    backup_main(option , path)


#*****************************************
def run_monitoring_scheduler(start_datetime, end_datetime):

    log_file = log_file_template.format(log_date=start_datetime.strftime("%Y-%m-%d"))

    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Scheduler daemon started")

    scheduler = BackgroundScheduler()

    # Task 1: Run every minute
    interval_trigger_1 = IntervalTrigger(minutes=1, start_date=start_datetime)
    scheduler.add_job(monitoring, interval_trigger_1)

    # Task 2: Run every 2 minutes
  #  interval_trigger_2 = IntervalTrigger(minutes=2, start_date=start_datetime)
  #  scheduler.add_job(report, interval_trigger_2)


    # Task: Run every day at 10:00 AM starting from a specific start_datetime
    cron_trigger = CronTrigger(hour=10, minute=0, start_date=start_datetime)
    scheduler.add_job(report, cron_trigger)


    scheduler.start()

    try:
        while True:
            if datetime.now() >= end_datetime:
                logging.info("End datetime reached. Shutting down Scheduler.")
                scheduler.shutdown()
                if os.path.exists(FIFO_FILE):
                    os.remove(FIFO_FILE)  # Remove the FIFO file when ending
                break
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        if os.path.exists(FIFO_FILE):
            os.remove(FIFO_FILE)  # Remove the FIFO file on exit

#*****************************************
def run_backup_scheduler(start_datetime, end_datetime, interval_minutes , option , path):

    log_file = log_file_template.format(log_date=start_datetime.strftime("%Y-%m-%d"))

    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Task 2 Scheduler daemon started")

    scheduler = BackgroundScheduler()

    interval_trigger = IntervalTrigger(minutes=interval_minutes, start_date=start_datetime)
    scheduler.add_job(backup, interval_trigger , args=(option,path))

    scheduler.start()

    try:
        while True:
            if datetime.now() >= end_datetime:
                logging.info("End datetime reached. Shutting down Task 2 Scheduler.")
                scheduler.shutdown()
                break
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
#*****************************************
def open_file_with_xdg(file_path):
    try:
        subprocess.run(['xdg-open', file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error opening file with xdg-open: {e}")
#*****************************************
def main():
    parser = argparse.ArgumentParser(
        description="A comprehensive script to manage system logs, performance reports, backups, and monitoring.\n"
                    "Use the options below to view logs, generate reports, or schedule backups and monitoring."
    )

    # Define main arguments
    parser.add_argument(
        '-l', type=str, metavar='<YYYY-MM-DD>', nargs='?', const=datetime.now().strftime("%Y-%m-%d"),
        help="View the log file for the specified date. Defaults to today's date if not provided."
    )
    parser.add_argument(
        '-r', type=str, metavar='<YYYY-MM-DD>', nargs='?', const=datetime.now().strftime("%Y-%m-%d"),
        help="View the daily performance report for the specified date. Defaults to today's date if not provided."
    )

    # Define system monitoring arguments
    parser.add_argument(
        '-m', action='store_true',
        help="Schedule system performance monitoring. Use with -end, -start, and -email."
    )
    parser.add_argument(
        '-email', type=str, metavar='<email>',
        help="Specify the email address to send alert notifications to. Defaults to jeneen348@gmail.com if not provided."
    )
    parser.add_argument(
        '-start', type=str, metavar='<YYYY-MM-DD HH:MM>',
        help="Specify the start date and time for the backup/monitoring. Defaults to the current date and time if not provided."
    )
    parser.add_argument(
        '-end', type=str, metavar='<YYYY-MM-DD HH:MM>',
        help="Specify the end date and time for the backup/monitoring."
    )

    # Define backup scheduling arguments
    parser.add_argument(
        '-b', action='store_true',
        help="Schedule a backup with specified start and end times, and the number of runs. Use with -path, -end, -start, and -numberofruns."
    )
    parser.add_argument(
        '-numberofruns', type=int, metavar='<N>',
        help="Specify the number of times the backup should run. Required with -b."
    )
    parser.add_argument(
        '-path', type=str, metavar='<path/tofile>',
        help="Specify the directory where the backup should start. Required with -b."
    )
#*****************************************
    # Parse arguments
    args = parser.parse_args()

    # Use the current date if no date is provided
    log_date = args.l if args.l else datetime.now().strftime("%Y-%m-%d")
    report_date = args.r if args.r else datetime.now().strftime("%Y-%m-%d")

    if not any([args.l, args.r, args.m, args.b]):
        parser.print_help()
        return
#*****************************************
    if args.l:
        log_file_path = log_file_template.format(log_date=log_date)
        print(f"Opening log file for date: {log_date}")
        if os.path.exists(log_file_path):
            open_file_with_xdg(log_file_path)
        else:
            print(f"Log file not found: {log_file_path}")
#*****************************************
    if args.r:
        report_file_path = report_file_template.format(report_date=report_date)
        print(f"Opening performance report file for date: {report_date}")
        if os.path.exists(report_file_path):
            open_file_with_xdg(report_file_path)
        else:
            print(f"Performance report file not found: {report_file_path}")
#*****************************************
    if args.m:
        start_time = args.start if args.start else datetime.now().strftime("%Y-%m-%d %H:%M")
        email = args.email if args.email else "jeneen348@gmail.com"
        if not args.end:
            parser.error("-end is required.")
        
        print(f"Scheduling system monitoring with start time {start_time}, end time {args.end}, and alert email {email}.")
        if os.path.exists(FIFO_FILE):
            print("Scheduler has already been started. Use -b to schedule additional tasks.")
            return

        start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(args.end, "%Y-%m-%d %H:%M")
        # Validate that start datetime is before end datetime
        if start_datetime >= end_datetime:
            parser.error("Start datetime must be before end datetime.")   

        # Create the FIFO
        os.mkfifo(FIFO_FILE)         

        with daemon.DaemonContext():
            run_monitoring_scheduler(start_datetime, end_datetime )
#***************************************************************
    if args.b:
        start_time = args.start if args.start else datetime.now().strftime("%Y-%m-%d %H:%M")
# Check if path is provided
        if not args.path:
            parser.error("-b requires -path")

        # Check if end time and number of runs are given together
        if not args.numberofruns:
            parser.error("-numberofruns is required.")
        if not args.end:
            parser.error("-end is required.")


        if os.path.isfile(args.path):
            option = "-f"
        elif os.path.isdir(args.path):
            option = "-d"
        else:
            parser.error("The provided path does not exist or is not a file/directory.")
        

        if args.end and args.numberofruns:
            # Calculate total minutes between start and end
            total_minutes = int((datetime.strptime(args.end, "%Y-%m-%d %H:%M") - datetime.strptime(start_time, "%Y-%m-%d %H:%M")).total_seconds() / 60)
            interval_minutes = total_minutes // args.numberofruns


        start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(args.end, "%Y-%m-%d %H:%M")
        if start_datetime >= end_datetime:
            parser.error("Start datetime must be before end datetime.")

                    
        with daemon.DaemonContext():
            run_backup_scheduler(start_datetime, end_datetime, interval_minutes , option ,args.path )
#***************************************************************
if __name__ == "__main__":
    main()

