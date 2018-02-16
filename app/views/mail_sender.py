import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(from_email, to_email, msg.as_string())
        server.close()
        print ("successfully sent the mail")
    except Exception as e:
        print ("failed to send mail " + str(e))
