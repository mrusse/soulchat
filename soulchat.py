import smtplib
import ssl
from email.message import EmailMessage
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

email = config["SMTP"]["email"]
password = config["SMTP"]["app_password"]
smtp_server = config["SMTP"]["smtp_server"]
smtp_port = int(config["SMTP"]["smtp_port"])
recipient = config["SMTP"]["recipient"]
use_ssl = config["SMTP"].getboolean("use_ssl", fallback=True)

msg = EmailMessage()
msg["Subject"] = "Soulchat Test"
msg["From"] = email
msg["To"] = recipient
msg.set_content("This is a test email Soulchat.")

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
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
