![banner](https://raw.githubusercontent.com/mrusse/soulchat/refs/heads/main/resources/banner.png)

<h1 align="center">Soulchat</h1>
<p align="center">
  A Python script to notify you of private chats from SoulseekQT or Nicotine+.
</p>

# About
Soulchat monitors your SoulseekQT and/or your Nicotine+ log directories and notifies you of new chats.
Current functionality is limited to sending notification emails when a new user that you do not have chat
history with messages you.

# Setup
First clone the repo or install the docker image. Docker image available at [mrusse08/soulchat](https://hub.docker.com/repository/docker/mrusse08/soulchat/general).
Then place your config file in the `/data` directory (relative to soulchat.py). Example config available [here](https://github.com/mrusse/soulchat/blob/main/config.ini).

You will need to update the config with your SMTP details. If using gmail all have need to change is the [app password](https://myaccount.google.com/apppasswords) and
the email you are sending/receiving from. 

You will also have to provide your SoulseekQT and/or Nicotine+ log file locations in the config file. As well as your username for the given client.

### Usual log folder locations:
```
SoulseekQT (Windows): %localappdata%\SoulseekQt\Soulseek Chat Logs\Users
SoulseekQT (Linux): /home/<user>/Soulseek Chat Logs/Users
Nicotine+ (Windows): %appdata%\nicotine\logs\private
Nicotine+ (Linux): /home/<user>/.local/share/nicotine/logs/private
```
Your logs may be in a different directory depending on your system.

## Example Docker Compose

```yml
version: "3.8"

services:
  soulchat:
    image: mrusse08/soulchat:latest
    container_name: soulchat
    restart: unless-stopped
    network_mode: bridge
    volumes:
      # Select where you are storing your config file.
      # Leave it mounted to "/data" since thats where the script expects the config file to be inside the container.
      - /mnt/user/appdata/soulchat:/data
      # Log file locations (you only need to set the paths for the clients you use).
      - /path/to/your/SoulseekQT/chat/logs:/SoulseekQT_Logs
      - /path/to/your/Nicotine+/chat/logs:/Nicotine+_Logs
    environment:
      - PUID=99
      - PGID=100
      - UMASK=000
      - TZ=Etc/UTC
```
Note: You **must** edit both log volumes in the docker compose above.

## Config file options

```ini
[General]
#How often it checks for new chats (in seconds)
script_interval = 300
#List of clients that you use. If you only use one client then only list one.
clients = SoulseekQT,Nicotine+

[SMTP]
email = your_email@gmail.com
#Retreive your gmail app password here: https://myaccount.google.com/apppasswords
#DO NOT post this password anywhere PLEASE!
app_password = abcdefghijklmnop
smtp_server = smtp.gmail.com
smtp_port = 465
recipient = your_email@gmail.com
use_ssl = true

#If you do not use one of the clients below feel free to remove the section from the config.
[SoulseekQT]
#Directory that is storing all the chat txt files. 
#If you are using docker then this should be the path that is mounted INSIDE the container.
log_directory = /SoulseekQT_Logs
#Your SoulseekQT username
username = Bob1234

[Nicotine+]
log_directory = /Nicotine+_Logs
#Your Nicotine+ username
username = Frank1234
```
