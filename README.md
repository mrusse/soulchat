![banner](https://raw.githubusercontent.com/mrusse/soulchat/refs/heads/main/resources/banner.png)

<h1 align="center">Soulchat</h1>
<p align="center">
  A Python script to notify you of private chats from SoulseekQT or Nicotine+.
</p>

# 04-24-2025: 
Pretty early WIP right now only works with the QT client and has basic functionality.
Need to update the config with your SMTP details. If using gmail all you need to change is the [app password](https://myaccount.google.com/apppasswords) and
the email you are sending and receiving to. The config file is currently expected to be at `/data/config.ini`

Docker image available at [mrusse08/soulchat](https://hub.docker.com/repository/docker/mrusse08/soulchat/general)

# Example Docker Compose

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
      # Leave "/data" since thats where the script expects the config file to be.
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
