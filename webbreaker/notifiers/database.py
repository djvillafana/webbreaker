import psycopg2
from webbreaker.webbreakerlogger import Logger
from webbreaker.notifiers.notifier import Notifier


class DatabaseNotifier(Notifier):

    def __init__(self, database_settings):
        self.connection_params = database_settings
        Notifier.__init__(self, "DatabaseNotifier")

    def notify(self, event):

        if self.connection_params:
            try:
                conn = psycopg2.connect(**self.connection_params)
                cur = conn.cursor()

                sql = "INSERT INTO event_demo (timestamp, scanid, scanname, event, server) VALUES " \
                      "(%(timestamp)s, %(scanid)s, %(scanname)s, %(event)s, %(server)s);"
                cur.execute(sql, event)

                conn.commit()
                cur.close()
                conn.close()
                Logger.file_logr.debug("Notification sent to database")
            except Exception as e: # we don't want failure to stop us, just note that it happened.
                Logger.file_logr.debug("Error inserting to database {0}".format(e.message))
        else: # we don't want failure to stop us, just note that it happened.
            Logger.file_logr.debug("Will not attempt database insert due to earlier error")

    def issue_export(self, issue):
        if self.connection_params:
            try:
                conn = psycopg2.connect(**self.connection_params)
                cur = conn.cursor()

                sql = "INSERT INTO issues (scanid, scanname, timestamp, issue) VALUES " \
                      "(%(scanid)s, %(scanname)s, %(timestamp)s, %(issue_json)s);"
                cur.execute(sql, issue)

                conn.commit()
                cur.close()
                conn.close()
                Logger.file_logr.debug("Issues sent to database")
            except Exception as e: # we don't want failure to stop us, just note that it happened.
                Logger.file_logr.debug("Error inserting to database {0}".format(e.message))
        else: # we don't want failure to stop us, just note that it happened.
            Logger.file_logr.debug("Will not attempt database insert due to earlier error")

    def __str__(self):
        return "DatabaseNotifier"
