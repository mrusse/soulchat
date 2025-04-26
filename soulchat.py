import os
import ssl
import time
import json
import logging
import smtplib
import configparser
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def send_email(subject, body, client_type):
    sc_footer = os.path.join(os.getcwd(), "resources", "banner.png")
    logo_footer = os.path.join(os.getcwd(), "resources", f"{client}.png")
    html_template_path = os.path.join(os.getcwd(), "resources", "email_template.html")

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = recipient

    with open(html_template_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("\n", "").replace("\t", "").replace("\r", "")
    html = html.replace("{{ body }}", body)

    msg.attach(MIMEText(html, "html"))

    if os.path.exists(sc_footer):
        with open(sc_footer, "rb") as img:
            img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<sc_footer>')
        msg.attach(image)

    if os.path.exists(logo_footer):
        with open(logo_footer, "rb") as img:
            img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<logo_footer>')
        msg.attach(image)

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
            send_email(email_subject, email_body, client_type)
        except Exception as e:
            logging.error(f"Failed to read or send {file}: {e}")

config_path = "/data/config.ini"

if not os.path.exists(os.getcwd() + config_path):
    raise FileNotFoundError(f"Missing config file at {os.getcwd()}{config_path}")

config = configparser.ConfigParser()
config.read(os.getcwd() + config_path)

script_interval = int(config["General"].getint("script_interval", fallback=300))
clients = [c.strip() for c in config.get("General", "clients").split(",")]

email = config["SMTP"]["email"]
password = config["SMTP"]["app_password"]
smtp_server = config["SMTP"]["smtp_server"]
smtp_port = int(config["SMTP"]["smtp_port"])
recipient = config["SMTP"]["recipient"]
use_ssl = config["SMTP"].getboolean("use_ssl", fallback=True)

while True:
    for client in clients:
        try:
            log_dir = config[client]["log_directory"]
            username = config[client]["username"]
            json_file = f"{os.getcwd()}/data/{client}.json"
            logging.info(f"Checking for new {client} chats...")

            load_json = os.path.exists(json_file)
            if not load_json:
                logging.info(f"{json_file} not found. Creating it now.")

            new_files = get_new_logs(log_dir, json_file, username)
            if not new_files:
                logging.info(f"No new {client} chats found.")
            else:
                for file in new_files:
                    logging.info(f"New {client} chat found: {os.path.basename(file)}")

            if load_json and new_files:
                batch_send_new_files(new_files, client)

        except Exception as e:
            logging.error(f"Error processing chat logs for {client}: {e}")

    logging.info(f"Sleeping for {script_interval} seconds...")
    time.sleep(script_interval)