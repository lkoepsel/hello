import logging
import requests
import socket
import os
import sys


hadtomount = False

if not os.path.exists('/boot/firmware'):
    hadtomount = True
    os.system("sudo mount /dev/mmcblk0p1 /boot/firmware")

# set logging to DEBUG, if not showing up
logging.basicConfig(filename='/boot/firmware/hello.log', encoding='utf-8',
                    format='%(asctime)s %(filename)s:%(levelname)s: %(message)s',
                    level=logging.DEBUG)

IP_file = "hello_ip.txt"  # Replace with your desired file name

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
            break  # Exit the loop if the file is found and opened successfully
        except IOError:
            logging.error("Error opening file: %s", file_path)
            sys.exit(0)
else:
    logging.error("%s not found in %s ", IP_file, dirs_to_check)
    sys.exit(0)

if hadtomount:
    os.system("sudo umount /boot/firmware")

host_name = socket.gethostname()
logging.debug("Host name: %s  ", host_name)

url = 'http://' + ip + '/receive'
text = f"{host_name}"
logging.debug(url)

data = {'text': text}

try:
    response = requests.post(url, data=data)

except requests.exceptions.RequestException as e:
    logging.error(e)
    sys.exit(1)

logging.debug(response.status_code)
logging.debug(response.text)
