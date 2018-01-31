import smtplib
import config

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
    def __init__(self):
        self.last_was_error = False

    def check_health(self, miner_instance):
        # If there are no warnings, lets bail out sooner.
        if not miner_instance.warnings and not miner_instance.errors:
            if self.last_was_error:
                # Send clearning email
                self.last_was_error = False
                send_email(config.GMAIL_USER, config.GMAIL_PWD, config.EMAIL_TO, "Antmonitor: Pass", "All miners are working properly. Go to {0} for verification".format(config.DOMAIN_ADDR))
            return True
        message = "Error founds while monitoring. Please go to {} \n {}\n".format(
            config.DOMAIN_ADDR, miner_instance)
        send_email(config.GMAIL_USER, config.GMAIL_PWD, config.EMAIL_TO, "Antmonitor: Alert for miner {}".format(miner_instance.miner.ip), message)
        self.last_was_error = True
        return False
