import smtplib
import os

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PWD = os.environ["GMAIL_PWD"]
EMAIL_TO = os.environ["EMAIL_TO"]
DOMAIN_ADDR = os.environ["DOMAIN_ADDR"]

def send_email(gmail_user, gmail_pwd, recipient, subject, body):
    from_email = gmail_user
    to_email = recipient if isinstance(recipient, list) else [recipient]
    subject = subject
    text = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (from_email, ", ".join(to_email), subject, text)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(from_email, to_email, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

class MinerReporter(object):
    def check_health(self, miner_instance):
        # If there are no warnings, lets bail out sooner.
        if not miner_instance.warnings and not miner_instance.errors:
            return True
        message = "Error founds while monitoring. Please go to {} \n {}\n".format(
            DOMAIN_ADDR, miner_instance)
        send_email(GMAIL_USER, GMAIL_PWD, EMAIL_TO, "Antmonitor: Alert for miner {}".format(miner_instance.miner.ip), message)
        return False
