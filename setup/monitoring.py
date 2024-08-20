#!/usr/bin/env python3
import psutil
import os
import logging
import subprocess
import argparse
from datetime import datetime, timedelta

# Define paths and thresholds
script_dir = os.path.dirname(os.path.abspath(__file__))
usage_data_file = os.path.join(script_dir, 'usage_data.txt')
log_file_template = os.path.expandvars("$HOME/Desktop/python/logfiles/system_monitor_{log_date}.log")
report_file_template = os.path.expandvars("$HOME/Desktop/python/system_reports/System_Performance_Report_{report_date}.txt")

# Define thresholds
CPU_THRESHOLD = 15
MEM_THRESHOLD = 80
DISK_THRESHOLD = 75
NETWORK_THRESHOLD = 100 * 1024 * 1024  # 100 MB

# Function to log messages
def log_message(message):
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = log_file_template.format(log_date=log_date)
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(message)s')
    logging.info(message)

# Function to send an email
def send_email(subject, body, to_email):
    try:
        command = ['/usr/bin/mail', '-s', subject, to_email]  
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        process.communicate(input=body.encode())
        print(f"Email sent to {to_email}")
        message = f"Email sent to: {to_email}"
        log_message(message)
    except Exception as e:
        print(f"Failed to send email: {e}")
        message = f"Failed to send email:{e}"
        log_message(message)


# Function to initialize the usage data file
def initialize_usage_data_file():
    if not os.path.exists(usage_data_file):
        with open(usage_data_file, 'w') as file:
            file.write('0 0 0 0 0\n')  # Initial totals and count of runs
            file.write(f"{datetime.min.isoformat()}\n")  # Initial last email time

# Function to read and update usage data
def update_usage_data(cpu, memory, disk, network):
    try:
        # Read current data
        if os.path.exists(usage_data_file):
            with open(usage_data_file, 'r') as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    data_line = lines[0].strip()
                    last_email_time = lines[1].strip()
                else:
                    data_line = '0 0 0 0 0'
                    last_email_time = '1970-01-01T00:00:00.000000'
        else:
            data_line = '0 0 0 0 0'
            last_email_time = '1970-01-01T00:00:00.000000'

        # Parse data
        totals = list(map(float, data_line.split()))
        total_cpu, total_memory, total_disk, total_network, num_runs = totals

        # Update totals
        total_cpu += cpu
        total_memory += memory
        total_disk += disk
        total_network += network
        num_runs += 1

        # Update file
        with open(usage_data_file, 'w') as file:
            file.write(f"{total_cpu} {total_memory} {total_disk} {total_network} {num_runs}\n")
            file.write(f"{last_email_time}\n")  # Do not update the last email time here

    except Exception as e:
        print(f"Failed to update usage data: {e}")

# Function to print alerts and send email with pause logic
def print_alert(message):
    print(f"ALERT: {message}")

    try:
        # Read the last email time from the file
        if os.path.exists(usage_data_file):
            with open(usage_data_file, 'r') as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    last_email_time_str = lines[1].strip()
                    last_email_time = datetime.fromisoformat(last_email_time_str)
                else:
                    last_email_time = datetime.min
        else:
            last_email_time = datetime.min

        # Check if 10 minutes have passed
        if datetime.now() - last_email_time >= timedelta(minutes=10):
            send_email("System Alert", message, 'jeneen348@gmail.com')
            # Update the last email time in the file
            with open(usage_data_file, 'r+') as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    lines[1] = f"{datetime.now().isoformat()}\n"
                else:
                    lines.append(f"{datetime.now().isoformat()}\n")
                file.seek(0)
                file.writelines(lines)
        else:
            print("Email not sent. Waiting period has not yet passed.")
            message = f"mail not sent. Waiting period has not yet passed."
            log_message(message)

            
    except Exception as e:
        print(f"Failed to handle alert: {e}")

# Health check functions
def check_cpu_usage(threshold=CPU_THRESHOLD):
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > threshold:
        message = f"High CPU usage detected: {cpu_usage}%"
        log_message(message)
        print_alert(message)
    return cpu_usage

def check_memory_usage(threshold=MEM_THRESHOLD):
    memory_usage = psutil.virtual_memory().percent
    if memory_usage > threshold:
        message = f"High memory usage detected: {memory_usage}%"
        log_message(message)
        print_alert(message)
    return memory_usage

def check_disk_space(path='/', threshold=DISK_THRESHOLD):
    disk_usage = psutil.disk_usage(path).percent
    if disk_usage > threshold:
        message = f"Low disk space detected: {disk_usage}%"
        log_message(message)
        print_alert(message)
    return disk_usage

def check_network_traffic(threshold=NETWORK_THRESHOLD):
    network_traffic = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
    if network_traffic > threshold:
        message = f"High network traffic detected: {network_traffic / (1024 * 1024):.2f} MB"
        log_message(message)
        print_alert(message)
    return network_traffic

# Function to run health checks
def run_health_checks():
    print("Monitoring the system...")
    log_message("Running system health checks...")

    # Initialize the usage data file if it does not exist
    initialize_usage_data_file()

    # Run health checks and get current data
    cpu_usage = check_cpu_usage()
    memory_usage = check_memory_usage()
    disk_usage = check_disk_space()
    network_traffic = check_network_traffic()

    log_message("Health checks completed.")

    # Update usage data after checks
    if os.path.exists(usage_data_file):
        update_usage_data(cpu_usage, memory_usage, disk_usage, network_traffic)
    else:
        print(f"Usage data file does not exist: {usage_data_file}")

def generate_report():
    try:
        # Read accumulated values and counts from the file
        if os.path.exists(usage_data_file):
            with open(usage_data_file, 'r') as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    data_line = lines[0].strip()
                    cpu_total, mem_total, disk_total, network_total, count = map(float, data_line.split())
                    count = int(count)  # Convert count to an integer
                else:
                    cpu_total = mem_total = disk_total = network_total = count = 0
        else:
            cpu_total = mem_total = disk_total = network_total = count = 0

        # Reset the usage file
        with open(usage_data_file, 'w') as file:
            file.write('0 0 0 0 0\n')  # Reset data and count

        # Calculate the averages
        avg_cpu = cpu_total / count if count else 0
        avg_mem = mem_total / count if count else 0
        avg_disk = disk_total / count if count else 0
        avg_network = network_total / count if count else 0

        # Prepare report file name with current date
        report_date = datetime.now().strftime("%Y-%m-%d")
     #   report_file = os.path.join(script_dir, f'System_Performance_Report_{report_date}.txt')
        report_file = report_file_template.format(report_date=report_date)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Write the performance data to the report file
        with open(report_file, 'w') as file:
            file.write(f"System Performance Report - {timestamp}\n")
            file.write("=====================================\n")
            file.write(f"Current CPU Usage: {psutil.cpu_percent(interval=1):.2f}%\n")
            file.write(f"Average CPU Usage: {avg_cpu:.2f}%\n")
            file.write("-------------------------------------\n")
            file.write(f"Current Memory Usage: {psutil.virtual_memory().percent:.2f}%\n")
            file.write(f"Average Memory Usage: {avg_mem:.2f}%\n")
            file.write("-------------------------------------\n")
            file.write(f"Current Disk Usage: {psutil.disk_usage('/').percent:.2f}%\n")
            file.write(f"Average Disk Usage: {avg_disk:.2f}%\n")
            file.write("-------------------------------------\n")
            file.write(f"Current Network Traffic: {(psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent) / (1024 * 1024):.2f} MB\n")
            file.write(f"Average Network Traffic: {avg_network / (1024 * 1024):.2f} MB\n")
            file.write("=====================================\n")

        print(f"System performance report generated: {report_file}")

    except Exception as e:
        print(f"Failed to generate report: {e}")


def main(option):


    # Execute the appropriate function based on the argument
    if (option==1):
        run_health_checks()
    else:
        generate_report()

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='System Performance Monitor')
    parser.add_argument('-c', '--run', action='store_true', help='Run the health checks')
    parser.add_argument('-r', '--generate', action='store_true', help='Generate performance report')
    args = parser.parse_args()

    # Execute the appropriate function based on the argument
    if args.run:
        option=1
    elif args.generate:
        option=2
    else:
        print("wrong option")
    main(option)