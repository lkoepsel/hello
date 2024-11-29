# hello - A Raspberry Pi Identity Solution

**Formerly know as rasp-mDNS**, *yeah, its clear why I changed the name.*

Recently, the Raspberry Pi Foundation released [Raspberry Pi Connect](https://www.raspberrypi.com/documentation/services/connect.html), which "*provides secure access to your Raspberry Pi from anywhere in the world.*" That's great, except for a couple of issues:
* You need to register. I understand why, however, its a burdensome step to solve such a simple problem.
* Its a *world-wide* solution. I was looking for a *local* solution, one which doesn't **require** connecting to the internet.
* And the deal-killer, it requires the full desktop install. If I need to connect to my Raspberry Pi, more often than not, its in a headless configuration. Headless and desktop are somewhat *antithetical*. 

**Update: July 4th, 2024**
Raspberry Pi has added the ability to perform this on a CLI OS, such as Bookworm (Lite), however, it still seems to be a bit much.

## Description
This is a solution for identifying newly programmed, headless *Raspberry Pi (RPi)*'s on a large network. In large networks (*ex: community college*), the wireless network has a significant issue. As network is quite large, it can be difficult to readily identify a *RPi* which has recently joined the network, therefore making it almost impossible to connect to the *RPi*.

## Easy Solution (*macOS* or *Linux*)
There are two, dead-simple, solutions which work well in **small networks** and on *macOS* or *Linux*. *Windows* unfortunately, doesn't do *Bonjour*.:

1. Use the *multicast DNS* service to attempt to connect. This uses the existing solution of [*avahi aka zeroconfig or Bonjour*](https://www.raspberrypi.com/documentation/computers/remote-access.html#resolving-raspberrypi-local-with-mdns) to connect with the *RPi*. It works quite well and is the best solution.

Using the username and hostname you used in programming the SD card with the *Pi Imager* application, try:
```bash
ssh username@hostname.local
```
In large networks this might take a while or not work at all. Worse yet, it doesn't always work. And when it doesn't work, there needs to be a remediation step.

2. To mitigate this issue, try this command: (*replace hostname with the name you provided when programming the SD card*). This command may work faster than attempting to login immediately.
```bash
dns-sd -G v4 hostname.local
```
Example Output:
```bash
DATE: ---Tue 13 Feb 2024---
16:32:22.348  ...STARTING...
Timestamp     A/R  Flags IF  Hostname      Address     TTL
16:32:51.715  Add  2.    17  pisan.local.  192.168.1.  120
```
Notice that the IP address is provided in the second line of *192.168.1.6*

```bash
# Connect to the board using the IP address
ssh 192.168.1.6
# after a warning regarding the "...authenticity of host..." and a few seconds, you will see the CLI prompt.
```

And the second step might not work, either. Leaving you with a *RPi*, which is on the network, however, you are unable to connect to it.

## The *hello* Solution - Run a service on Raspberry Pi
The next solution is to implement an auto-connecting application on startup, on the remote *RPi*. This application will ping a local server (your PC or another host *RPi*) with its host name and IP address. This ensures you have ready access to the remote *RPi* without having to go through determining its IP address again.

This solution will work due to the ability to save your server's IP address on the *RPi*, prior to boot. This means the *RPi* is trying to find you, instead of vice-versa. 

Once implemented, the steps to connect in a new network are:
1. Determine your host system (your PC) IP address in the new network
2. Using any platform, Windows, macOS or Linux, enter the IP address into a specific file on the *RPi* SD Card.
3. Place the SD Card in the RPi and power it up. Start the hello_server application on your host system and wait for the *ping*.

## Installation
### 1. Requirements
#### 1.1 Host System (Your PC or a host *RPi*)
*Python* and the *flask* library. If you don't have *flask* installed and encounter the new Python requirement to run in a virtual environment...you may install it system-wide with *sudo apt install python3-flask* on *Debian* (or *Raspberry Pi Bookworm*).

#### 1.2. Raspberry Pi (remote *RPi*)
Raspberry Pi OS Bookworm (or later)

### 2. Create a hello.service on the remote Raspberry Pi
Create a startup application, which will ping a server by *IP address* and report **its own** host name and IP address.

#### 2.1.. Create hello.py
This is the program which executes as part of the *hello.service*. Open a Python file, then copy/paste contents below into file:
```python
# open a file named hello.py
sudo nano /usr/bin/hello.py
```
Paste the following contents then Ctrl-S, to save and Ctrl-X to exit *nano*.
```python
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
text = f"{host_name}"  # Just send the hostname without "hello from"
logging.debug(url)

data = {'text': text}

try:
    response = requests.post(url, data=data)

except requests.exceptions.RequestException as e:
    logging.error(e)
    sys.exit(1)

logging.debug(response.status_code)
logging.debug(response.text)

```
*Ctrl-S* (save) *Ctrl-X* (exit)

#### 2.2. Add IP address of the host server to the remote *RPi* boot folder
This step identifies your PC by IP address to the Raspberry Pi:

1. You may run either server program (*simple_server.py or hello_server.py*), and it will report the host IP address. 
1. Open a the file to contain the IP address.

```bash
sudo nano /boot/firmware/hello_ip.txt
```

Enter the only the numeric IP address of your PC WITHOUT a return at the end of the line. The file *hello_ip.txt* will need to look like:

```bash
192.168.1.124:5000
```
*Ctrl-S* (save) *Ctrl-X* (exit)

**Note:** By storing the IP address in a file at */boot/firmware*, you may access the file on a macOS or Windows system. The *boot/firmware* folder shows up as a readable folder on either system called *bootfs*. This enables you to change the IP address on your PC then re-insert the SD Card into the *RPi* to ping you at a new address. 

There is also a file on *boot/firmware* called *hello.log*, which you can open with a text editor. It will contain the log entries for the *hello.service*. Use these entries if you are having difficulty getting a ping from the *RPi.* 

#### 2.3. Setup `systemd` unit file for hello.py service
This will execute the hello.py app, after all other startup services have been executed on the RPi. 

The service will log entries to */boot/firmware/hello.log* on the *RPi* or */bootfs/hello.log* when examining the SD Card on a Mac/Windows system. Use it to determine any issues with the service.

You may also use the command `journalctl -b`, to see all boot messages of the *RPi*. or use `journalctl -b | grep hello`, to see all messages related to the service.

You can use the space bar, to quickly go through screens of lines. Look for the word DEBUG as the *hello.py* application uses logging to print messages.

#### hello.service
Same as above, use nano to create file, copy/paste contents below then exit *nano*. **Be sure to change *username* to what is appropriate for your system.
```bash
sudo nano /lib/systemd/system/hello.service
```

Copy/paste contents below into the file:
```bash
[Unit]
Description=Ping a known server (hello_ip.txt) with hostname and IP address
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python /usr/bin/hello.py
Restart=on-failure
RestartSec=1
StartLimitInterval=0
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
```

Exit nano using *Ctrl-S* *Ctrl-X*

Run the following commands to create service and test it. (*Go to step 4 and confirm the hello message appears*):
```bash
sudo chmod 644 /lib/systemd/system/hello.service
sudo systemctl daemon-reload
# enable the service so that it runs on all subsequent systems boots
sudo systemctl start hello.service
sudo systemctl status hello.service
```

**It is important to enable the service to run on startup.**
```bash
# if hello.service is running well, then enable to run on boot
sudo systemctl enable hello.service
```

Additional commands which will be helpful, later once the service is running:
```bash
# determine if the hello.service is running
sudo systemctl status hello.service

# stop the hello.service, useful if you want to stop pinging server
sudo systemctl stop hello.service

# restart the hello.service, this will stop then start the service
sudo systemctl restart hello.service
```
## Pick 3a or 3b below based on your needs.
### 3a. Simple Version (Good for single *RPi* connections)
The simple version is useful for single *RPi* connections. Using a terminal program on your PC, use one tab to connect to your hello_server system (typically a host *RPi* or your PC) and the second tab to connect to the remote *RPi* in question. Once this repository is installed on the host *RPi*, follow the steps below:
1. Run `python -m simple_server` on the host *RPi*.
2. Ensure the remote *RPi* has the hello.service running.
3. Reboot the remote *RPi*.

In your host tab, once the remote *RPi* has been rebooted, you should see the following:
```bash
...
* Running on http://192.168.1.49:5000
...
speedy
192.168.1.112 - - [29/Nov/2024 08:54:40] "POST / HTTP/1.1" 200 -
```

The *running on* message is the IP address of the server *RPi* and the two lines with *speedy* are the hostname and IP address of the remote *RPi*.

### 3b. Enhanced Version with Database: Run hello_server.py
This enhanced version stores all connections in a SQLite database and provides a web interface showing hostnames, IP addresses, and timestamps. It includes several improvements:

- Persistent storage of connections in a SQLite database
- Local time display for each connection
- Clean web interface using MVP.css
- Command line options for cleaning database of old entries

#### Installation

The server can be started with the following options:
```bash
# Normal start
python hello_server.py

# Reset database (clears all entries)
python hello_server.py --reset
```

#### Features
- **Database Storage**: All connections are stored in a SQLite database (`messages.db`)
- **Local Time**: Timestamps are stored and displayed in local time
- **Web Interface**: Clean, responsive interface showing:
  - Hostname
  - IP Address
  - Last Update (MM/DD/YYYY HH:MM format)
- **Database Management**:
  - Automatic cleanup of test entries
  - Command line option to reset database
  - Persistent storage between server restarts

#### Security Notes
- The server listens on all network interfaces (0.0.0.0) to allow LAN connections
- Only runs on the local network, not exposed to the internet
- Database is stored locally and can be reset if needed

### NOTES
#### Permissions Issue
If you might get the following response:
```bash
python3 -m hello_server
 * Serving Flask app 'hello_server'
 * Debug mode: on
Permission denied
```

In the example above, I've changed the port from 80, the typical *http* port, which requires sudo permissions to *5000*.

#### Install Flask
If you need to install *flask*, and get the new *externally-managed-environment* as in:
```bash
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install....
```

I recommend you follow the advice on a Linux system and simply use *sudo apt install python3-flask*, to install *flask*.
 
#### Example Output of hello_server.py:
```bash
python serverv2.py
 * Serving Flask app 'serverv2'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:80
 * Running on http://192.168.1.124:80
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 101-330-852
pitwo
192.168.1.76 - - [10/Feb/2024 16:16:36] "POST / HTTP/1.1" 200 -
pitwo
192.168.1.76 - - [10/Feb/2024 16:17:29] "POST / HTTP/1.1" 200 -
pisan
192.168.1.76 - - [11/Feb/2024 06:46:41] "POST / HTTP/1.1" 200 -
```
## Initial instance
There is a "chicken/egg" problem which can occur. If you can't initially connect to the *RPi*, how do you add the *hello* solution?

1. My immediate solution is to connect 1:1 with the Raspberry Pi, using an ethernet cable. This creates a two element network, my PC and my *RPi*. Then apply the steps above.
2. Next up from that is to initially use the *RPi* in a small network, where its easier to connect.
3. A third solution is to create an installable image which already contains the hello service. The make this the standard image you use, going forward. I'll detail the steps here:
### Creating a Raspberry Pi OS hello image
*You will need to do this in a small network or tightly coupled setup as described in solution #1 above.*

1. Use Pi Imager to write the Raspberry Pi OS Lite (64-bit) to an SD Card or USB drive. In the OS Customization tab, I've provided the hostname of *hello* and as I know it will be my image, I add my publickey on the Services tab.
2. Once written, I put the SD Card into my *RPi*, wait for it to boot sufficiently then login `ssh hello.local`.
3. I follow the steps above, and once I've confirmed the service works well. I create a new image:
### Saving, shrinking and sending an image
I use a Linux laptop to perform the following steps. You can use your Raspberry Pi, however, you will need several smaller USB drives to hold the images prior to shrinking them.
```bash
# remove SD Card or USB drive containing RPi image and place in Linux PC
# determine physical device
lsblk
# find specific drive "sdc", "sdd" which is the right size of RPi drive, use as input
sudo dd if=/dev/sdb of=./pibuildv3.img bs=1M status=progress
# shrink the size of the image to save space
sudo pishrink.sh -avz pibuildv3.img
wormhole send pibuildv3.img.gz
```

## Notes
1. If the *RPi* isn't connecting, it might be a problem with startup. The service logs to */boot/firmware/hello.log*.  If you are unable to access the Pi, you may shutdown the *RPi* and examine the file via a Mac or Windows system. It will be at the root level of the */bootfs* folder.
1. If you are able to access the Pi, you may `cat /boot/firmware/hello.log` or use `journalctl -b | grep hello` to examine the startup log for *hello.service* entries. 
1. Implementing the optional solution, allows you to change networks and identify your PC's new IP address. Mount the SD card on your PC and edit /bootfs/hello_ip.txt, replacing the IP address with the new one. Put the SD card back into the *RPi*, run `python hello_server.py` then boot the *RPi*. It will ping your server with its new address.
1. If you have multiple *RPI*'s and want to confirm which one is which, run `sudo du -h /`, which prints the size of all folders to the screen. This will make the green led light for several seconds.
1. When using *RPi Imager* software, use *Shift-Ctrl-X* to bring up the options screen.
1. Once you've confirmed you no longer need the *RPi* pinging the server, you can stop it with *sudo systemctl stop hello.service*. The service is designed to stop running once it has successfully pinged a server.
1. As Windows has difficulty using *Bonjour*, you could consider nmap as an alternative to identify *Raspberry Pi*'s on your network. [nmap Windows Version](https://nmap.org/download.html#windows)