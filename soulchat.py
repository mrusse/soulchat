import os
import ssl
import time
import json
import logging
import smtplib
import configparser
from email.message import EmailMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = recipient
    msg.set_content(body)

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(email, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                smtp.login(email, password)
                smtp.send_message(msg)
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")    

def get_new_logs(log_dir, json_file, username):
    username = f"[{username}]"

    current_files = [
        f for f in os.listdir(log_dir)
        if os.path.isfile(os.path.join(log_dir, f))
    ]
    
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            previous_files = json.load(f)
    else:
        previous_files = []

    new_files = []
    
    for f in current_files:
        if f not in previous_files:
            full_path = os.path.join(log_dir, f)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file:
                    contents = file.read()
                    if username not in contents:
                        new_files.append(full_path)
            except Exception as e:
                logging.warning(f"Could not read {f}: {e}")

    with open(json_file, "w") as f:
        json.dump(current_files, f, indent=2)

    return new_files

def get_username(file, client_type):
    try:
        with open(file, "r", encoding="utf-8") as f:
            line = f.readline()
            if client_type == "SoulseekQT":
                return line.split("]")[1][1:]
            elif client_type == "Nicotine+":
                return line.split("[")[1].split("]")[0]
    except Exception as e:
        logging.warning(f"Could not extract username from {file}: {e}")
        return "Unknown"

def batch_send_new_files(new_files, client_type):
    for file in new_files:
        email_body = ""
        username = get_username(file, client_type)
        email_subject = f"New {client_type} Message From: {username}"

        try:
            with open(file, "r", encoding="utf-8") as f:
                email_body = f.read()
            send_email(email_subject, email_body)
        except Exception as e:
            logging.error(f"Failed to read or send {file}: {e}")

config_path = "/data/config.ini"

if not os.path.exists(config_path):
    raise FileNotFoundError("Missing config file at /data/config.ini")

config = configparser.ConfigParser()
config.read(config_path)

script_interval = int(config["General"].getint("script_interval", fallback=300))

email = config["SMTP"]["email"]
password = config["SMTP"]["app_password"]
smtp_server = config["SMTP"]["smtp_server"]
smtp_port = int(config["SMTP"]["smtp_port"])
recipient = config["SMTP"]["recipient"]
use_ssl = config["SMTP"].getboolean("use_ssl", fallback=True)

qt_log_dir = config["SoulseekQT"]["log_directory"]
qt_json = "/data/SoulseekQT.json"
qt_username = config["SoulseekQT"]["username"]

while True:
    logging.info("Checking for new chats...")

    load_json = os.path.exists(qt_json)
    if not load_json:
        logging.info(f"{qt_json} not found. Creating it now.")

    new_files = get_new_logs(qt_log_dir, qt_json, qt_username)
    if not new_files:
        logging.info("No new chats found.")
    else:
        for file in new_files:
            logging.info(f"New chat found: {os.path.basename(file)}")

    if load_json and new_files:
        batch_send_new_files(new_files, "SoulseekQT")

    logging.info(f"Sleeping for {script_interval} seconds...")
    time.sleep(script_interval)