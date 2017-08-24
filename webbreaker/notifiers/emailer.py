#!/usr/bin/env python


try:
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
except ImportError: #Python3
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
import smtplib
from webbreaker.notifiers.notifier import Notifier
from webbreaker.webbreakerlogger import Logger


class EmailNotifier(Notifier):
    def __init__(self, emailer_settings):
        self.emailer_settings = emailer_settings
        Notifier.__init__(self, "EmailNotifier")

    def notify(self, event):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.emailer_settings['from_address']
            msg['To'] = self.emailer_settings['to_address']
            msg['Subject'] = "{0} {1}".format(event['subject'], event['scanname'])

            html = str(self.emailer_settings['email_template']).format(event['server'],
                                                                      event['scanname'],
                                                                      event['scanid'],
                                                                      event['subject'],
                                                                      "".join(
                                                                          ["<li>{0}</li>".format(t) for t in event['targets']]))
            msg.attach(MIMEText(html, 'html'))

            mail_server = smtplib.SMTP(self.emailer_settings['smtp_host'], self.emailer_settings['smtp_port'])
            mail_server.sendmail(msg['From'], msg['To'], msg.as_string())

            mail_server.quit()
        except Exception as e:  # we don't want email failure to stop us, just log that it happened
            Logger.file_logr.error("Problem sending email. {0}".format(e.message))

    def __str__(self):
        return "EmailNotifier"
