import time
from datetime import datetime, timedelta, date

from uniquebible import config


class DateUtil:

    # Return naive datetime object in UTC
    @staticmethod
    def utcNow():
        return datetime.utcnow()

    # Return current epoch time
    @staticmethod
    def epoch():
        return int(time.time())
        # return int(time.mktime(time.gmtime()))

    # Return current local date
    # 2021-02-23
    @staticmethod
    def localDateNow():
        return datetime.now().date()

    # Return date object when string in format "2021-02-23"
    @staticmethod
    def dateStringToObject(d):
        return datetime.strptime(d, '%Y-%m-%d').date()

    # Add days to date object
    @staticmethod
    def addDays(date, days):
        return date + timedelta(days=days)

    # Return current local date in current language format
    @staticmethod
    def formattedLocalDateNow(format="short"):
        return DateUtil.formattedLocalDate(DateUtil.localDateNow(), format)

    # Return date in current language format
    @staticmethod
    def formattedLocalDate(date, format="short"):
        from babel.dates import format_date

        return format_date(date, format=format, locale=config.displayLanguage[:2])

    # Parse date string in language format into date object
    @staticmethod
    def parseDate(date):
        from babel.dates import parse_date

        return parse_date(date, locale=config.displayLanguage[:2])

    # Convert datetime to UTC epoch datetime
    @staticmethod
    def datetimeToEpoch(dt):
        return int(dt.strftime('%s'))

    # Convert struct_time to epoch
    @staticmethod
    def stimeToEpoch(t):
        return time.mktime(t)

    # Seconds between local timezone and UTC timezone
    @staticmethod
    def secondsBetweenLocalAndUtc():
        return int(DateUtil.stimeToEpoch(time.gmtime()) - DateUtil.stimeToEpoch(time.localtime()))

    @staticmethod
    def currentYear():
        return date.today().year

    @staticmethod
    def currentMonth():
        return date.today().month

    @staticmethod
    def currentDay():
        return date.today().day

    @staticmethod
    def monthFullName(month):
        return datetime.strptime(str(month), "%m").strftime("%B")

def test_epoch():
    print(DateUtil.epoch())
    print(time.gmtime())
    print(time.localtime())
    print(DateUtil.stimeToEpoch(time.gmtime()))
    print(DateUtil.stimeToEpoch(time.localtime()))

    diff = DateUtil.secondsBetweenLocalAndUtc()
    print(diff)

def test_formats():
    config.displayLanguage = "en_US"
    dateStr = DateUtil.formattedLocalDateNow()
    print(dateStr)
    # 2/23/21
    config.displayLanguage = "zh"
    dateStr = DateUtil.formattedLocalDateNow()
    print(dateStr)
    # 2021/2/23
    config.displayLanguage = "de"
    dateStr = DateUtil.formattedLocalDateNow()
    print(dateStr)
    # 23.02.21
    dateObj = DateUtil.parseDate(dateStr)
    print(dateObj)
    # 2021-02-23
    print(DateUtil.localDateNow())
    # 2021-02-23

def test_addDays():
    now = DateUtil.localDateNow()
    print(now)
    later = DateUtil.addDays(now, 7)
    print(later)

def test_stringFormat():
    dateObj = DateUtil.dateStringToObject('2021-02-23')
    print(dateObj)

def test_month():
    dateObj = DateUtil.monthFullName(1)
    print(dateObj)

if __name__ == "__main__":
    test_month()
