from __future__ import absolute_import, division, print_function, unicode_literals

from .log import Log
from .alert_contact import AlertContact
from termcolor import colored


class Monitor(object):
    class Type:
        HTTP = 1
        KEYWORD = 2
        PING = 3
        PORT = 4

    TYPES = {
        Type.HTTP: "http(s)",
        Type.KEYWORD: "keyword",
        Type.PING: "ping",
        Type.PORT: "port",
    }

    class Subtype:
        HTTP = 1
        HTTPS = 2
        FTP = 3
        SMTP = 4
        POP3 = 5
        IMAP = 6
        CUSTOM = 99


    SUBTYPES = {
        Subtype.HTTP: "http",
        Subtype.HTTPS: "https",
        Subtype.FTP: "ftp",
        Subtype.SMTP: "smtp",
        Subtype.POP3: "pop3",
        Subtype.IMAP: "imap",
        Subtype.CUSTOM: "custom",
    }

    class KeywordType:
        EXISTS = 1
        NOT_EXISTS = 2

    KEYWORD_TYPES = {
        KeywordType.EXISTS: "exists",
        KeywordType.NOT_EXISTS: "not exists",
    }

    class Status:
        PAUSED = 0
        NOT_CHECKED_YET = 1
        UP = 2
        SEEMS_DOWN = 8
        DOWN = 9

    STATUSES = {
        Status.PAUSED: "paused",
        Status.NOT_CHECKED_YET: "not checked yet",
        Status.UP: "up",
        Status.SEEMS_DOWN: "seems down",
        Status.DOWN: "down",
    }

    def __init__(self, data, custom_uptime_ratio_periods=[]):
        self.alert_contacts = [AlertContact(ac) for ac in data.get("alertcontact", [])]
        self.logs = [Log(log) for log in data.get("log", [])]
        self.custom_uptime_ratio_periods = custom_uptime_ratio_periods

        self.id = data["id"]
        self.name = data["friendlyname"]
        self.url = data["url"]
        self.type = int(data["type"])
        self.subtype = int(data["subtype"]) if data["subtype"] else None

        self.keyword_type = int(data["keywordtype"]) if data["keywordtype"] else None
        self.keyword = data["keywordvalue"]

        self.http_username = data["httpusername"]
        self.http_password = data["httppassword"]
        self.port = int(data["port"]) if data["port"] else None

        self.status = int(data["status"])
        self.all_time_uptime_ratio = float(data["alltimeuptimeratio"])

        if "customuptimeratio" in data:
            self.custom_uptime_ratio = [float(n) for n in data["customuptimeratio"].split("-")]
        else:
            self.custom_uptime_ratio = []


    @property
    def subtype_str(self):
        if self.subtype:
            return self.SUBTYPES[self.subtype]
        else:
            return None

    keyword_type_str = property(lambda self: self.KEYWORD_TYPES[self.keyword_type])
    type_str = property(lambda self: self.TYPES[self.type])
    status_str = property(lambda self: self.STATUSES[self.status])


    def dump(self):
        if self.status in [self.Status.UP]:
            color = "green"
        elif self.status in [self.Status.SEEMS_DOWN, self.Status.DOWN]:
            color = "red"
        else:
            color = "yellow"

        status = colored(self.status_str.title(), color)
        print("%s [%s] #%s" % (self.name, status, self.id))

        if self.port:
            print("URL: %s:%d" % (self.url, self.port))
        else:
            print("URL: %s" % self.url)


        if self.http_username:
            print("User: %s (%s)" % self.http_username, self.http_password)

        print("Type: %s" % self.type_str)

        if self.subtype:
            print("Subtype: %s" % self.subtype_str)

        print("All Time Uptime Ratio:         %.2f%%" % self.all_time_uptime_ratio)

        if self.custom_uptime_ratio:
            for period, ratio in zip(self.custom_uptime_ratio_periods, self.custom_uptime_ratio):
                str = "Uptime Ratio over %d hour%s:" % (period, "" if period == 1 else "s")
                print("%-30s %.2f%%" % (str, ratio))

        if self.keyword_type:
            print("Keyword: %s (%s)" % (self.keyword, self.keyword_type_str))

        if self.alert_contacts:
            print()
            print("Alert contacts:")
            for alert in self.alert_contacts:
                alert.dump()

        if self.logs:
            print()
            print("Log:")
            for log in self.logs:
                log.dump()
                print()