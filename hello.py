import logging
import requests
import socket
import os
import sys


def setup_logging():
    try:
        # Check if /boot/firmware is mounted
        hadtomount = False
        if not os.path.exists("/boot/firmware"):
            hadtomount = True
            mount_result = os.system("sudo mount /dev/mmcblk0p1 /boot/firmware")
            if mount_result != 0:
                print("ERROR: Failed to mount /boot/firmware", file=sys.stderr)
                sys.exit(10)  # Exit code 10: Mount failure

        # set logging to DEBUG, if messages aren't seen in log file
        logging.basicConfig(
            filename="/home/lkoepsel/hello.log",
            encoding="utf-8",
            format="%(asctime)s %(filename)s:%(levelname)s: %(message)s",
            level=logging.DEBUG,
        )

        return hadtomount
    except PermissionError:
        print("ERROR: Permission denied when setting up logging", file=sys.stderr)
        sys.exit(11)  # Exit code 11: Logging permission error
    except Exception as e:
        print(f"ERROR: Failed to setup logging: {str(e)}", file=sys.stderr)
        sys.exit(12)  # Exit code 12: General logging setup error


def find_ip_file():
    IP_file = "hello_ip.txt"  # Name of the file containing the IP address
    # List of directories to search
    dirs_to_check = ["/boot", "/boot/firmware"]

    # Search for the file in the listed directories
    for dir_path in dirs_to_check:
        file_path = os.path.join(dir_path, IP_file)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r") as f:
                    ip = f.read().rstrip("\n")
                    logging.debug("IP address found in %s", file_path)
                return ip  # Return IP if found
            except IOError as e:
                logging.error("Error opening file: %s - %s", file_path, str(e))
                print(f"ERROR: Could not read {file_path}: {str(e)}", file=sys.stderr)
                sys.exit(20)  # Exit code 20: File read error

    # If we get here, file wasn't found
    error_msg = f"{IP_file} not found in {dirs_to_check}"
    logging.error(error_msg)
    print(f"ERROR: {error_msg}", file=sys.stderr)
    sys.exit(21)  # Exit code 21: IP file not found


def main():
    try:
        # Setup logging and mount if needed
        hadtomount = setup_logging()

        # Find IP address
        ip = find_ip_file()

        # Unmount if we mounted
        if hadtomount:
            umount_result = os.system("sudo umount /boot/firmware")
            if umount_result != 0:
                logging.warning("Failed to unmount /boot/firmware")

        # Get hostname and prepare request
        host_name = socket.gethostname()
        logging.debug("Host name: %s", host_name)

        url = "http://" + ip
        text = f"{host_name}"  # send hostname
        logging.debug("Sending request to: %s", url)

        data = {"text": text}

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses

            logging.debug("Status code: %s", response.status_code)
            logging.debug("Response: %s", response.text)
            return 0  # Success

        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error to {url}: {str(e)}"
            logging.error(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return 30  # Exit code 30: Connection error

        except requests.exceptions.Timeout as e:
            error_msg = f"Request timed out to {url}: {str(e)}"
            logging.error(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return 31  # Exit code 31: Timeout

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from {url}: {str(e)}"
            logging.error(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return 32  # Exit code 32: HTTP error

        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed to {url}: {str(e)}"
            logging.error(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return 33  # Exit code 33: General request error

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        # Try to log if logging is set up
        try:
            logging.error(error_msg)
        except:
            pass
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return 99  # Exit code 99: Unexpected error


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
