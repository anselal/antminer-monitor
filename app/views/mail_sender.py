import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import logger
import config


def send_email(gmail_user, gmail_pwd, to_email, subject, body_html, body_plain):
    from_email = gmail_user
    subject = subject
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.attach(MIMEText(body_plain, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))

    # Send actual message
    try:
        logger.debug("Sending email...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(from_email, to_email, msg.as_string())
        server.close()
        logger.debug ("Successfully sent the mail")
        return True
    except Exception as e:
        logger.error ("Failed to send mail " + str(e))
        return False
