import time
from datetime import timezone


class DateUtil:

    # Return current epoch time
    def epoch():
        return int(time.time())
        # return int(time.mktime(time.gmtime()))

    # Convert datetime to UTC epoch datetime
    def datetime_to_epoch(dt):
        return int(dt.strftime('%s'))

    # Convert struct_time to epoch
    def stime_to_epoch(t):
        return time.mktime(t)

    def seconds_between_local_and_utc():
        return int(DateUtil.stime_to_epoch(time.gmtime()) - DateUtil.stime_to_epoch(time.localtime()))

def test1():
    print(DateUtil.epoch())
    print(time.gmtime())
    print(time.localtime())
    print(DateUtil.stime_to_epoch(time.gmtime()))
    print(DateUtil.stime_to_epoch(time.localtime()))

    diff = DateUtil.seconds_between_local_and_utc()
    print(diff)

if __name__ == "__main__":

    test1()
